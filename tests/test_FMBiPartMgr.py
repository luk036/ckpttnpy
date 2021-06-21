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
    read_json
)

Part = Union[Dict[Any, int], List[int]]


def run_FMBiPartMgr(H: Netlist, part: Part):
    gainMgr = FMBiGainMgr(FMBiGainCalc, H)
    constrMgr = FMBiConstrMgr(H, 0.3, H.module_weight)
    partMgr = FMPartMgr(H, gainMgr, constrMgr)
    partMgr.legalize(part)
    totalcostbefore = partMgr.totalcost
    partMgr.init(part)
    assert partMgr.totalcost == totalcostbefore
    partMgr.optimize(part)
    assert partMgr.totalcost <= totalcostbefore


def test_FMBiPartMgr():
    H = create_test_netlist()
    part = {v: 0 for v in H}
    run_FMBiPartMgr(H, part)


def test_FMBiPartMgr2():
    H = create_drawf()
    part = {v: 0 for v in H}
    H.module_fixed = {'p1'}
    run_FMBiPartMgr(H, part)


def test_FMBiPartMgr3():
    H = read_json('testcases/p1.json')
    part = [0 for _ in H]
    run_FMBiPartMgr(H, part)


def test_FMBiPartMgr4():
    H = create_random_hgraph()
    part = [0 for _ in H]
    run_FMBiPartMgr(H, part)
