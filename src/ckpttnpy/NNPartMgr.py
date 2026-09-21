"""No-Nonsense Partition Manager — greedy local-search refinement.

``NNPartMgr`` is a :class:`PartMgrBase` subclass that performs greedy
hill-climbing without FM's sophisticated search machinery.  It overrides only
the single-pass hook: it repeatedly takes the highest-gain move from the gain
buckets while the gain stays positive, so it never snapshots/rolls back and
never locks a moved module (a selected module simply leaves the buckets for the
rest of the pass).  ``init``/``legalize``/``optimize``/``final_check`` are
inherited unchanged from :class:`PartMgrBase`.
"""

from .PartMgrBase import Part, PartMgrBase


class NNPartMgr(PartMgrBase):
    """No-Nonsense Partitioning Manager (greedy local search)."""

    def _optimize_1pass(self, part: Part) -> None:
        """Greedily move the highest-gain module while its gain is positive."""
        totalgain = 0
        while not self.gain_mgr.is_empty():
            move_info_v, gainmax = self.gain_mgr.select(part)
            if gainmax <= 0:
                break
            if not self.validator.check_constraints(move_info_v):
                continue
            v, _, to_part = move_info_v
            self.gain_mgr.update_move(part, move_info_v)
            self.gain_mgr.update_move_v(move_info_v, gainmax)
            self.validator.update_move(move_info_v)
            totalgain += gainmax
            part[v] = to_part
        self.totalcost -= totalgain
