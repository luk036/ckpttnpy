"""
PartMgrBase.py

This code defines a base class called PartMgrBase that manages partitioning in a graph-like structure.
The purpose of this code is to provide a foundation for implementing the Fiduccia-Mattheyses
partitioning algorithm, which is used to divide elements (like modules in a circuit) into different
groups while optimizing certain criteria.

The class takes three main inputs when initialized: a hypergraph (which represents the structure to
be partitioned), a gain manager (which handles the gains associated with moving elements between
partitions), and a constraint manager (which ensures the partitioning follows certain rules).

While the code doesn't directly produce an output, it modifies the input partitioning (represented
by the part parameter in various methods) to improve it according to the algorithm's criteria.
The main goal is to reduce the total cost of the partitioning while maintaining legal constraints.

The class achieves its purpose through several key methods:

1. init: This method initializes the partitioning process by setting up the initial total cost and
   preparing the gain manager and constraint validator.

2. legalize: This method attempts to make an illegal partitioning legal by moving elements between
   partitions. It repeatedly selects the best move (with the highest gain) that improves the legality
   of the partition until no more improvements can be made or all constraints are satisfied.

3. optimize: This method repeatedly calls _optimize_1pass to improve the partitioning until no
   further improvements can be made.

4. _optimize_1pass: This is the core optimization method. It iteratively selects the best move
   (with the highest gain) and applies it to the partitioning. It also keeps track of the best
   solution seen so far and can revert to that solution if the optimization starts to worsen the result.

The algorithm works by maintaining a list of possible moves, each with an associated gain
(improvement in the total cost). It repeatedly selects and applies the best move, updating the
gains of affected elements after each move. This process continues until no more beneficial moves
are available.

An important aspect of the algorithm is its ability to make some temporarily unfavorable moves
(with negative gain) in hopes of finding a better overall solution later. This is achieved by taking
"snapshots" of good solutions and potentially reverting to them if the optimization doesn't pan out.

The code uses abstract methods (take_snapshot and restore_part_info) which are meant to be implemented in derived classes to handle the specifics of how partitioning information is saved and restored.

Overall, this code provides a flexible framework for implementing partition optimization algorithms, allowing for different strategies in managing gains, constraints, and the underlying graph structure.
"""

# Take a snapshot when a move make **negative** gain.
# Snapshot in the form of "interface"???
from abc import abstractmethod
from typing import Any, Dict, List, Union

from .FMConstrMgr import LegalCheck

Part = Union[Dict[Any, int], List[int]]


# The `PartMgrBase` class is a base class that manages parts, including their hierarchy, gain, and
# constraints.
class PartMgrBase:
    """Base class for Fiduccia-Mattheyses Partitioning Manager

    The `PartMgrBase` class is a base class that manages parts, including their hierarchy, gain, and
    constraints.
    """

    def __init__(self, hyprgraph, gain_mgr, constr_mgr):
        """
        The function initializes an object with three arguments and sets their values as attributes of the
        object.

        :param hyprgraph: The `hyprgraph` parameter is an object of type `hyprgraph` which is used for some purpose in the
            class. The specific purpose is not mentioned in the code snippet provided
        :param gain_mgr: The `gain_mgr` parameter is an object of type `gain_mgr`. It is used to manage the
            gains of the system
        :param constr_mgr: The `constr_mgr` parameter is an object of type `constr_mgr`. It is used to
            manage constraints in the code
        """
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
            return self.hyprgraph.module_weight.get(v, 1)
        return self.hyprgraph.get_module_weight(v)

    def init(self, part: Part):
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

    def legalize(self, part: Part):
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
            lambda v: self.get_module_weight(v) == 0
            and self.hyprgraph.module_fixed is False,
            self.hyprgraph,
        ):
            self.gain_mgr.lock_all(part[v], v)

        legalcheck = LegalCheck.NotSatisfied

        while legalcheck != LegalCheck.AllSatisfied:  # satisfied:
            # Take the gainmax with v from gainbucket

            # gainmax = self.gain_mgr.gainbucket.get_max()

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

    def optimize(self, part: Part):
        """
        The `optimize` function iteratively optimizes the cost of a given part until no further improvement
        can be made.

        :param part: The "part" parameter is an object of type "Part". It is used as input for the
            optimization process
        :type part: Part
        """
        while True:
            self.init(part)
            totalcostbefore = self.totalcost
            self._optimize_1pass(part)
            assert self.totalcost <= totalcostbefore
            if self.totalcost == totalcostbefore:
                break

    def _optimize_1pass(self, part: Part):
        """

        The `_optimize_1pass` function optimizes the placement of parts by selecting moves with the maximum

        gain and updating the placement accordingly.



        :param part: The `part` parameter represents a specific partition or group of elements. It is used

            in the context of a partitioning algorithm where elements are divided into different groups or

            partitions based on certain criteria

        :type part: Part



        .. svgbob::



            "Optimization Pass with Backtracking"

          +--------------------------+--------------------------+

          | Initial: gain=0          | Best: gain=+15           |

          | [A,A,B,B,C,C]            | [A,B,B,B,C,C]            |

          | Cost: 100                | Cost: 85                 |

          +--------------------------+--------------------------+

          | Exploring: gain=+5,-10   | Backtrack to best        |

          | [A,B,B,B,C,C] -> [A,B,C,B,C,C]  | gain=+15 preserved |

          +--------------------------+--------------------------+



          Algorithm explores moves, tracks best solution, and backtracks if needed

        """

        totalgain = 0

        deferredsnapshot = False

        snapshot = None

        besttotalgain = 0

        while not self.gain_mgr.is_empty():
            # Take the gainmax with v from gainbucket

            move_info_v, gainmax = self.gain_mgr.select(part)

            # Check if the move of v can satisfied or NotSatisfied

            satisfiedOK = self.validator.check_constraints(move_info_v)

            if not satisfiedOK:
                continue

            if gainmax < 0:
                # become down turn

                if (not deferredsnapshot) or (totalgain > besttotalgain):
                    # Take a snapshot before move

                    snapshot = self.take_snapshot(part)

                    besttotalgain = totalgain

                deferredsnapshot = True

            elif totalgain + gainmax >= besttotalgain:
                besttotalgain = totalgain + gainmax

                deferredsnapshot = False

            # Update v and its neigbours (even they are in waitinglist)

            # Put neigbours to bucket

            v, _, to_part = move_info_v

            self.gain_mgr.lock(to_part, v)

            self.gain_mgr.update_move(part, move_info_v)

            self.gain_mgr.update_move_v(move_info_v, gainmax)

            self.validator.update_move(move_info_v)

            totalgain += gainmax

            part[v] = to_part

        if deferredsnapshot:
            # restore previous best solution

            self.restore_part_info(snapshot, part)

            totalgain = besttotalgain

        self.totalcost -= totalgain

    @abstractmethod
    def take_snapshot(self, part: Part):
        """
        The `take_snapshot` function is an abstract method that takes a `Part` object as an argument and
        returns a value.

        :param part: The "part" parameter is of type "Part" and is used to specify the part of the system
            for which a snapshot needs to be taken
        :type part: Part
        """

    @abstractmethod
    def restore_part_info(self, snapshot, part: Part):
        """
        The function `restore_part_info` restores the information of a specific part from a given snapshot.

        :param snapshot: A snapshot of the part's information that needs to be restored. This could be a
            dictionary, object, or any other data structure that contains the necessary information to restore
            the part
        :param part: The "part" parameter is of type "Part"
        :type part: Part
        """
