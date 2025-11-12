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
            >>> mgr = FMBiConstrMgr([0, 1, 2], 0.3, [1, 1, 1])
            >>> mgr.diff = [10, 20]
            >>> mgr.select_togo()
            0
            >>> mgr.diff = [20, 10]
            >>> mgr.select_togo()
            1
        """
        return 0 if self.diff[0] < self.diff[1] else 1
