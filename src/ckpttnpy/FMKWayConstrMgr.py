# -*- coding: utf-8 -*-

from typing import Any, Dict, List, Union

# Check if the move of v can satisfied, makebetter, or notsatisfied
from .FMConstrMgr import FMConstrMgr, LegalCheck

Part = Union[Dict[Any, int], List[int]]


class FMKWayConstrMgr(FMConstrMgr):
    def __init__(self, H, BalTol, K: int):
        """[summary]

        Arguments:
            H (type):  description
            BalTol (type):  description
        """
        FMConstrMgr.__init__(self, H, BalTol, K)
        self.illegal = list(True for _ in range(K))

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
        return min(range(self.K), key=lambda k: self.diff[k])

    def check_legal(self, move_info_v):
        """[summary]

        Arguments:
            fromPart (type):  description
            v (type):  description

        Returns:
            dtype:  description
        """
        status = FMConstrMgr.check_legal(self, move_info_v)
        if status != LegalCheck.allsatisfied:
            return status

        _, fromPart, toPart = move_info_v
        self.illegal[fromPart] = self.illegal[toPart] = False
        if any(self.illegal):
            return LegalCheck.getbetter  # get better, but still illegal
        return LegalCheck.allsatisfied  # all satisfied
