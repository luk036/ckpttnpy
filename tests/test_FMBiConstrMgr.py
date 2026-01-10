import pytest

from ckpttnpy.FMBiConstrMgr import FMBiConstrMgr


@pytest.mark.parametrize(
    "diff, expected", [([10, 20], 0), ([20, 10], 1), ([10, 10], 1)]
)
def test_select_togo(diff, expected) -> None:
    hyprgraph = [0, 1, 2]
    module_weight = [1, 1, 1]
    mgr = FMBiConstrMgr(hyprgraph, 0.3, module_weight)
    mgr.diff = diff
    assert mgr.select_togo() == expected
