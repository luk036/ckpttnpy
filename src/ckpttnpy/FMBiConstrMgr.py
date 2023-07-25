from .FMConstrMgr import FMConstrMgr


class FMBiConstrMgr(FMConstrMgr):
    """The `FMBiConstrMgr` class is a subclass of `FMConstrMgr` that overrides the `select_togo` method to
    return 0 if `diff[0]` is less than `diff[1]`, otherwise it returns 1.
    """

    def select_togo(self) -> int:
        """
        The function `select_togo` returns 0 if the first element of `self.diff` is less than the second
        element, otherwise it returns 1.
        :return: an integer value.

        Examples:
            >>> fm = FMBiConstrMgr()
            >>> fm.diff = [1, 2]
            >>> fm.select_togo()
            1
            >>> fm.diff = [2, 1]
            >>> fm.select_togo()
            0
            >>> fm.diff = [1, 1]
            >>> fm.select_togo()
            0
            >>> fm.diff = [1, 0]
            >>> fm.select_togo()
            1
            >>> fm.diff = [0, 1]
            >>> fm.select_togo()
            1
            >>> fm.diff = [0, 0]
            >>> fm.select_togo()
            0
            >>> fm.diff = [0, -1]
            >>> fm.select_togo()
            1
            >>> fm.diff = [-1, 0]
            >>> fm.select_togo()
            1
            >>> fm.diff = [-1, -1]
            >>> fm.select_togo()
        """
        return 0 if self.diff[0] < self.diff[1] else 1
