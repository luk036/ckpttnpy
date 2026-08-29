"""No-Nonsense Partition Manager.

NNPartMgr is a :class:`PartMgrBase` subclass that performs FM-style partition
optimization without backtracking. It overrides only ``_optimize_1pass``:
unlike FM it accepts only positive-gain moves and stops at the first
non-improving move (no journal/snapshot rollback). The shared skeleton
(``init``/``legalize``/``optimize``/``final_check``) is inherited from
``PartMgrBase``.
"""

from .PartMgrBase import Part, PartMgrBase


class NNPartMgr(PartMgrBase):
    """No-Nonsense Partitioning Manager

    Inherits the FM algorithm skeleton from `PartMgrBase`; the only difference
    from `FMPartMgr` is the single-pass behaviour: stop at the first
    non-positive-gain move instead of journaling and rolling back.
    """

    def _optimize_1pass(self, part: Part) -> None:
        """Performs one pass of optimization, selecting positive-gain moves
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
