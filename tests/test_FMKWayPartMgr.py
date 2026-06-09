import pytest
from netlistx.netlist import (  # create_test_netlist,
    Netlist,
    create_drawf,
    create_random_hgraph,
    read_json,
)

from ckpttnpy.FMConstrMgr import LegalCheck
from ckpttnpy.FMKWayConstrMgr import FMKWayConstrMgr
from ckpttnpy.FMKWayGainCalc import FMKWayGainCalc
from ckpttnpy.FMKWayGainMgr import FMKWayGainMgr
from ckpttnpy.FMPartMgr import FMPartMgr
from ckpttnpy.skeleton import _logger
from tests.mocks import Part


def _run_FMKWayPartMgr(hyprgraph: Netlist, gain_mgr, num_parts, part: Part):
    """[summary]

    Arguments:
        hyprgraph (Netlist):  description
        gain_mgr (gain_mgr):  description
        num_parts (int):  number of partitions
    """
    constr_mgr = FMKWayConstrMgr(
        hyprgraph, 0.45, hyprgraph.module_weight, num_parts
    )  # 0.2 ???
    part_mgr = FMPartMgr(hyprgraph, gain_mgr, constr_mgr)
    legal_check = part_mgr.legalize(part)  # TODO
    if legal_check != LegalCheck.AllSatisfied:
        _logger.warning(f"Partitioning is not legal: {legal_check}")
    assert legal_check == LegalCheck.AllSatisfied
    totalcostbefore = part_mgr.totalcost
    part_mgr.init(part)
    assert part_mgr.totalcost == totalcostbefore
    part_mgr.optimize(part)
    assert part_mgr.final_check(part)
    assert part_mgr.totalcost <= totalcostbefore
    totalcostbefore = part_mgr.totalcost
    part_mgr.init(part)
    assert part_mgr.totalcost == totalcostbefore
    # print(part_mgr.snapshot)


@pytest.mark.parametrize(
    "create_netlist, num_parts, part_type",
    [
        (create_drawf, 3, dict),
        # (create_test_netlist, 3, dict),
        (create_random_hgraph, 3, list),
        (lambda: read_json("testcases/p1.json"), 5, list),
    ],
)
def test_FMKWayPartMgr(create_netlist, num_parts, part_type) -> None:
    hyprgraph = create_netlist()
    gain_mgr = FMKWayGainMgr(FMKWayGainCalc, hyprgraph, num_parts)
    if create_netlist == create_drawf:
        hyprgraph.module_fixed = {"p1"}
    part: Part
    if part_type is dict:
        part = {v: 0 for v in hyprgraph}
    else:
        part = [0 for _ in hyprgraph]
    _run_FMKWayPartMgr(hyprgraph, gain_mgr, num_parts, part)
