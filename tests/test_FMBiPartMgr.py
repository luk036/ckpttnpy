from typing import Any, Dict, List, Union

from ckpttnpy.FMBiConstrMgr import FMBiConstrMgr
from ckpttnpy.FMBiGainCalc import FMBiGainCalc
from ckpttnpy.FMBiGainMgr import FMBiGainMgr
from ckpttnpy.FMPartMgr import FMPartMgr
from ckpttnpy.netlist import (
    Netlist,
    create_drawf,
    create_random_hgraph,
    create_test_netlist,
    read_json,
)

Part = Union[Dict[Any, int], List[int]]


def run_FMBiPartMgr(hgr: Netlist, part: Part):
    gain_mgr = FMBiGainMgr(FMBiGainCalc, hgr)
    constrMgr = FMBiConstrMgr(hgr, 0.3, hgr.module_weight)
    part_mgr = FMPartMgr(hgr, gain_mgr, constrMgr)
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
    hgr = create_drawf()
    part = {v: 0 for v in hgr}
    hgr.module_fixed = {"p1"}
    run_FMBiPartMgr(hgr, part)


def test_FMBiPartMgr2():
    hgr = create_test_netlist()
    part = {v: 0 for v in hgr}
    run_FMBiPartMgr(hgr, part)


def test_FMBiPartMgr3():
    hgr = create_random_hgraph()
    part = [0 for _ in hgr]
    run_FMBiPartMgr(hgr, part)


def test_FMBiPartMgr4():
    hgr = read_json("testcases/p1.json")
    part = [0 for _ in hgr]
    run_FMBiPartMgr(hgr, part)
