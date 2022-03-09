# -*- coding: utf-8 -*-

from typing import Any, Dict, List, Union

# Check if the move of v can satisfied, makebetter, or NotSatisfied
from .FMConstrMgr import FMConstrMgr, LegalCheck

Part = Union[Dict[Any, int], List[int]]


class FMKWayConstrMgr(FMConstrMgr):
    def __init__(self, hgr, bal_tol, module_weight, num_parts: int):
        """[summary]

        Arguments:
            hgr (type):  description
            bal_tol (type):  description
        """
        FMConstrMgr.__init__(self, hgr, bal_tol, module_weight, num_parts)
        self.illegal = list(True for _ in range(num_parts))

    def init(self, part: Part):
        """[summary]

        Arguments:
            part (type):  description
        """
        FMConstrMgr.init(self, part)
        self.illegal = [d < self.lowerbound for d in self.diff]

    def select_togo(self):
        # minb = min(self.diff)
        # return self.diff.index(minb)
        return min(range(self.num_parts), key=lambda k: self.diff[k])

    def check_legal(self, move_info_v):
        """[summary]

        Arguments:
            from_part (type):  description
            v (type):  description

        Returns:
            dtype:  description
        """
        status = FMConstrMgr.check_legal(self, move_info_v)
        if status != LegalCheck.AllSatisfied:
            return status

        _, from_part, to_part = move_info_v
        self.illegal[from_part] = self.illegal[to_part] = False
        if any(self.illegal):
            return LegalCheck.GetBetter  # get better, but still illegal
        return LegalCheck.AllSatisfied  # all satisfied
