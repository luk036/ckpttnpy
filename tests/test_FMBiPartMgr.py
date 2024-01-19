from typing import Any, Dict, List, Union

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

Part = Union[Dict[Any, int], List[int]]


def run_FMBiPartMgr(hyprgraph: Netlist, part: Part):
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


def test_FMBiPartMgr():
    hyprgraph = create_drawf()
    part = {v: 0 for v in hyprgraph}
    hyprgraph.module_fixed = {"p1"}
    run_FMBiPartMgr(hyprgraph, part)


def test_FMBiPartMgr2():
    hyprgraph = create_test_netlist()
    part = {v: 0 for v in hyprgraph}
    run_FMBiPartMgr(hyprgraph, part)


def test_FMBiPartMgr3():
    hyprgraph = create_random_hgraph()
    part = [0 for _ in hyprgraph]
    run_FMBiPartMgr(hyprgraph, part)


def test_FMBiPartMgr4():
    hyprgraph = read_json("testcases/p1.json")
    part = [0 for _ in hyprgraph]
    run_FMBiPartMgr(hyprgraph, part)
