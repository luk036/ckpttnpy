import unittest
from ckpttnpy.FMConstrMgr import FMConstrMgr, LegalCheck


class MockHyprgraph:
    def __init__(self, num_modules):
        self.modules = range(num_modules)

    def __iter__(self):
        return iter(self.modules)


class TestFMConstrMgr(unittest.TestCase):
    def setUp(self):
        self.hyprgraph = MockHyprgraph(4)
        self.module_weight = [1, 1, 1, 1]
        self.mgr = FMConstrMgr(self.hyprgraph, 0.25, self.module_weight)

    def test_check_legal(self):
        part = [0, 0, 1, 1]
        self.mgr.init(part)
        # self.mgr.diff is [2, 2]
        # self.mgr.lowerbound is 1

        move_info_v = (0, 0, 1)  # move vertex 0 from part 0 to part 1
        legal = self.mgr.check_legal(move_info_v)
        self.assertEqual(legal, LegalCheck.AllSatisfied)

        self.mgr.update_move(move_info_v)
        # self.mgr.diff is [1, 3]
        move_info_v = (1, 0, 1)
        legal = self.mgr.check_legal(move_info_v)
        self.assertEqual(legal, LegalCheck.NotSatisfied)

        move_info_v = (2, 1, 0)
        legal = self.mgr.check_legal(move_info_v)
        self.assertEqual(legal, LegalCheck.AllSatisfied)

    def test_check_constraints(self):
        part = [0, 0, 1, 1]
        self.mgr.init(part)
        # self.mgr.diff is [2, 2]
        # self.mgr.lowerbound is 1

        move_info_v = (0, 0, 1)
        self.assertTrue(self.mgr.check_constraints(move_info_v))

        self.mgr.update_move(move_info_v)
        # self.mgr.diff is [1, 3]
        move_info_v = (1, 0, 1)
        self.assertFalse(self.mgr.check_constraints(move_info_v))

    def test_update_move(self):
        part = [0, 0, 1, 1]
        self.mgr.init(part)
        # self.mgr.diff is [2, 2]

        move_info_v = (0, 0, 1)
        self.mgr.weight = self.mgr.get_module_weight(move_info_v[0])
        self.mgr.update_move(move_info_v)
        self.assertEqual(self.mgr.diff, [1, 3])


if __name__ == "__main__":
    unittest.main()
