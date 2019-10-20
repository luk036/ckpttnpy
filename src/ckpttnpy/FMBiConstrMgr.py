# -*- coding: utf-8 -*-

# Check if the move of v can satisfied, makebetter, or notsatisfied
from .FMConstrMgr import FMConstrMgr


class FMBiConstrMgr(FMConstrMgr):
    # def __init__(self, H, BalTol, K=2):
    #     """[summary]

    #     Arguments:
    #         H (type):  description
    #         BalTol (type):  description
    #     """
    #     FMConstrMgr.__init__(self, H, BalTol, 2)

    def select_togo(self):
        """[summary]

        Returns:
            dtype:  description
        """
        return 0 if self.diff[0] < self.diff[1] else 1
