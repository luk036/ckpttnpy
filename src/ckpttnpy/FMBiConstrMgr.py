# -*- coding: utf-8 -*-

# Check if the move of v can satisfied, makebetter, or notsatisfied
from .FMConstrMgr import FMConstrMgr


class FMBiConstrMgr(FMConstrMgr):
    def select_togo(self):
        """[summary]

        Returns:
            dtype:  description
        """
        return 0 if self.diff[0] < self.diff[1] else 1
