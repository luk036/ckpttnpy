# -*- coding: utf-8 -*-

from typing import Any, Dict, List, Union

# Check if the move of v can satisfied, makebetter, or notsatisfied
from .FMConstrMgr import FMConstrMgr

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
        for k in range(self.K):
            self.illegal[k] = (self.diff[k] < self.lowerbound)

    def select_togo(self):
        minb = min(self.diff)
        return self.diff.index(minb)

    def check_legal(self, move_info_v):
        """[summary]

        Arguments:
            fromPart (type):  description
            v (type):  description

        Returns:
            dtype:  description
        """
        status = FMConstrMgr.check_legal(self, move_info_v)
        if status != 2:
            return status

        fromPart, toPart, _ = move_info_v
        self.illegal[fromPart] = self.illegal[toPart] = False
        if any(self.illegal):
            return 1  # get better, but still illegal
        return 2  # all satisfied
