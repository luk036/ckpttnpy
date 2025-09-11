import unittest

from ckpttnpy.FMBiConstrMgr import FMBiConstrMgr


class TestFMBiConstrMgr(unittest.TestCase):
    def test_select_togo(self):
        hyprgraph = [0, 1, 2]
        module_weight = [1, 1, 1]
        mgr = FMBiConstrMgr(hyprgraph, 0.3, module_weight)
        mgr.diff = [10, 20]
        assert mgr.select_togo() == 0
        mgr.diff = [20, 10]
        assert mgr.select_togo() == 1
        mgr.diff = [10, 10]
        assert mgr.select_togo() == 1
