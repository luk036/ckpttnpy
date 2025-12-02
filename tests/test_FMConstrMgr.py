import pytest
from ckpttnpy.FMConstrMgr import FMConstrMgr, LegalCheck


class MockHyprgraph:
    def __init__(self, num_modules):
        self.modules = range(num_modules)

    def __iter__(self):
        return iter(self.modules)


@pytest.fixture
def mgr():
    hyprgraph = MockHyprgraph(4)
    module_weight = [1, 1, 1, 1]
    return FMConstrMgr(hyprgraph, 0.25, module_weight)


def test_check_legal(mgr):
    part = [0, 0, 1, 1]
    mgr.init(part)
    # mgr.diff is [2, 2]
    # mgr.lowerbound is 1

    move_info_v = (0, 0, 1)  # move vertex 0 from part 0 to part 1
    assert mgr.check_legal(move_info_v) == LegalCheck.AllSatisfied

    mgr.update_move(move_info_v)
    # mgr.diff is [1, 3]
    move_info_v = (1, 0, 1)
    assert mgr.check_legal(move_info_v) == LegalCheck.NotSatisfied

    move_info_v = (2, 1, 0)
    assert mgr.check_legal(move_info_v) == LegalCheck.AllSatisfied


def test_check_constraints(mgr):
    part = [0, 0, 1, 1]
    mgr.init(part)
    # mgr.diff is [2, 2]
    # mgr.lowerbound is 1

    move_info_v = (0, 0, 1)
    assert mgr.check_constraints(move_info_v)

    mgr.update_move(move_info_v)
    # mgr.diff is [1, 3]
    move_info_v = (1, 0, 1)
    assert not mgr.check_constraints(move_info_v)


def test_update_move(mgr):
    part = [0, 0, 1, 1]
    mgr.init(part)
    # mgr.diff is [2, 2]

    move_info_v = (0, 0, 1)
    mgr.weight = mgr.get_module_weight(move_info_v[0])
    mgr.update_move(move_info_v)
    assert mgr.diff == [1, 3]
