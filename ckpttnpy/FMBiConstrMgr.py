# Check if the move of v can satisfied, makebetter, or notsatisfied
from .FMConstrMgr import FMConstrMgr


class FMBiConstrMgr(FMConstrMgr):
    def __init__(self, H, ratio):
        """[summary]

        Arguments:
            H {[type]} -- [description]
            ratio {[type]} -- [description]
        """
        FMConstrMgr.__init__(self, H, ratio, 2)

    def select_togo(self):
        """[summary]

        Returns:
            [type] -- [description]
        """
        return 0 if self.diff[0] < self.diff[1] else 1
