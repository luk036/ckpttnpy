import pytest
from netlistx.netlist import (
    Netlist,
    create_drawf,
    create_random_hgraph,
    create_test_netlist,
    read_json,
)

from ckpttnpy.FMBiConstrMgr import FMBiConstrMgr
from ckpttnpy.FMBiGainCalc import FMBiGainCalc
from ckpttnpy.FMBiGainMgr import FMBiGainMgr
from ckpttnpy.FMPartMgr import FMPartMgr

from tests.mocks import Part


def _run_FMBiPartMgr(hyprgraph: Netlist, part: Part) -> None:
    gain_mgr = FMBiGainMgr(FMBiGainCalc, hyprgraph)
    constr_mgr = FMBiConstrMgr(hyprgraph, 0.3, hyprgraph.module_weight)
    part_mgr = FMPartMgr(hyprgraph, gain_mgr, constr_mgr)
    part_mgr.legalize(part)
    totalcostbefore = part_mgr.totalcost
    part_mgr.init(part)
    assert part_mgr.totalcost == totalcostbefore
    part_mgr.optimize(part)
    assert part_mgr.totalcost <= totalcostbefore
    totalcostbefore = part_mgr.totalcost
    part_mgr.init(part)
    assert part_mgr.totalcost == totalcostbefore


@pytest.mark.parametrize(
    "create_netlist, part_type",
    [
        (create_drawf, dict),
        (create_test_netlist, dict),
        (create_random_hgraph, list),
        (lambda: read_json("testcases/p1.json"), list),
    ],
)
def test_FMBiPartMgr(create_netlist, part_type) -> None:
    hyprgraph = create_netlist()
    if part_type is dict:
        part = {v: 0 for v in hyprgraph}
    else:
        part = [0 for _ in hyprgraph]

    if create_netlist == create_drawf:
        hyprgraph.module_fixed = {"p1"}

    _run_FMBiPartMgr(hyprgraph, part)
