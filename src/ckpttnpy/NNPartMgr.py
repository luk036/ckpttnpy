"""No-Nonsense Partition Manager.

NNPartMgr implements a simplified FM-style partition optimization without
backtracking (no snapshot/restore). Unlike PartMgrBase, _optimize_1pass
only accepts positive-gain moves and stops at the first non-improving move.
"""

from typing import Any, Dict, List, Union

from .FMConstrMgr import LegalCheck

Part = Union[Dict[Any, int], List[int]]


# The `NNPartMgr` class is a base class that manages parts, including their hierarchy, gain, and
# constraints.
class NNPartMgr:


    def __init__(self, hyprgraph: Any, gain_mgr: Any, constr_mgr: Any):

        self.hyprgraph = hyprgraph
        self.gain_mgr = gain_mgr
        self.validator = constr_mgr
        self.num_parts = gain_mgr.num_parts
        self.totalcost = 0

    def get_module_weight(self, v: Any) -> int:
        """Get module weight for a given module.

        Args:
            v (Any): module name

        Returns:
            int: module weight
        """
        if isinstance(self.hyprgraph.module_weight, dict):
            weight = self.hyprgraph.module_weight.get(v, 1)
            assert isinstance(weight, int), f"Expected int, got {type(weight)}"
            return weight
        weight = self.hyprgraph.get_module_weight(v)
        assert isinstance(weight, int), f"Expected int, got {type(weight)}"
        return weight

    def init(self, part: Part) -> None:
        """
        The `init` function initializes the `totalcost` attribute and calls the `init` method of the
        `gain_mgr` and `validator` objects.

        :param part: The "part" parameter is of type "Part" and it represents some kind of part object
        :type part: Part

        .. svgbob::

            "Initial Partition State"
          +----------------+----------------+
          |  A  |  A  |  B  |  A  |  B  |  B  |
          | v1  | v2  | v3  | v4  | v5  | v6  |
          +----------------+----------------+

          Total cost calculation based on connections between partitions
        """
        self.totalcost = self.gain_mgr.init(part)
        assert self.totalcost >= 0
        self.validator.init(part)

    def legalize(self, part: Part) -> LegalCheck:
        """
        The `legalize` function is used to perform a legalization process on a given part in a graph.

        :param part: The `part` parameter represents the current partitioning of the modules. It is a data
            structure that assigns each module to a specific partition
        :type part: Part
        :return: The function `legalize` returns the value of the variable `legalcheck`.

        .. svgbob::

            "Before Legalization"      "After Legalization"
          +------------------+      +------------------+
          |  A   |  B   |  C  |    |  A   |  B   |  C  |
          | w=50 | w=20 | w=5 | -> | w=30 | w=30 | w=20 |
          +------------------+    +------------------+

          Move modules from over-weighted partitions to under-weighted ones
        """
        self.init(part)

        # Zero-weighted modules does not contribute legalization
        for v in filter(
            lambda v: (
                self.get_module_weight(v) == 0 and self.hyprgraph.module_fixed is False
            ),
            self.hyprgraph,
        ):
            self.gain_mgr.lock_all(part[v], v)

        legalcheck = LegalCheck.NotSatisfied
        while legalcheck != LegalCheck.AllSatisfied:  # satisfied:
            # Take the gainmax with v from gainbucket
            to_part = self.validator.select_togo()
            if self.gain_mgr.gainbucket[to_part]._max == 0:  # is_empty_togo()
                break
            v, gainmax = self.gain_mgr.select_togo(to_part)
            from_part = part[v]
            assert from_part != to_part
            move_info_v = v, from_part, to_part

            # Check if the move of v can NotSatisfied, makebetter, or satisfied
            legalcheck = self.validator.check_legal(move_info_v)
            if legalcheck == LegalCheck.NotSatisfied:  # NotSatisfied
                continue

            # Update v and its neigbours (even they are in waitinglist)
            # Put neigbours to bucket
            self.gain_mgr.update_move(part, move_info_v)
            self.gain_mgr.update_move_v(move_info_v, gainmax)
            self.validator.update_move(move_info_v)
            part[v] = to_part
            self.totalcost -= gainmax
            assert self.totalcost >= 0
        return legalcheck

    def optimize(self, part: Part) -> None:

        while True:
            self.init(part)
            totalcostbefore = self.totalcost
            self._optimize_1pass(part)
            assert self.totalcost <= totalcostbefore
            if self.totalcost == totalcostbefore:
                break
        # return legalcheck
        assert self.totalcost <= totalcostbefore

    def _optimize_1pass(self, part: Part) -> None:
        """
        Performs one pass of optimization, selecting positive-gain moves
        until no further improvement is possible (stops at first non-positive gain).

        :param part: The partition assignment to optimize
        :type part: Part
        """
        totalgain = 0

        while not self.gain_mgr.is_empty():
            # Take the gainmax with v from gainbucket
            move_info_v, gainmax = self.gain_mgr.select(part)

            if gainmax <= 0:
                break

            # Check if the move of v can satisfied or NotSatisfied
            satisfiedOK = self.validator.check_constraints(move_info_v)
            if not satisfiedOK:
                continue

            # Update v and its neigbours (even they are in waitinglist)
            # Put neigbours to bucket
            v, _, to_part = move_info_v
            self.gain_mgr.update_move(part, move_info_v)
            self.gain_mgr.update_move_v(move_info_v, gainmax)
            self.validator.update_move(move_info_v)
            totalgain += gainmax
            part[v] = to_part

        self.totalcost -= totalgain

    def final_check(self, part: Part) -> bool:

        return bool(self.validator.final_check(part))
