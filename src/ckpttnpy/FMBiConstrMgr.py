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
        """
        return 0 if self.diff[0] < self.diff[1] else 1
