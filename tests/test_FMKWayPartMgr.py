from typing import Any, Dict, List, Union

from ckpttnpy.FMKWayConstrMgr import FMKWayConstrMgr
from ckpttnpy.FMKWayGainCalc import FMKWayGainCalc
from ckpttnpy.FMKWayGainMgr import FMKWayGainMgr
from ckpttnpy.FMPartMgr import FMPartMgr
from ckpttnpy.netlist import (
    Netlist,
    create_drawf,
    create_random_hgraph,
    create_test_netlist,
    read_json,
)

Part = Union[Dict[Any, int], List[int]]


def run_FMKWayPartMgr(hgr: Netlist, gainMgr, num_parts, part: Part):
    """[summary]

    Arguments:
        hgr (Netlist):  description
        gainMgr (gainMgr):  description
        num_parts (int):  number of partitions
    """
    constrMgr = FMKWayConstrMgr(hgr, 0.4, hgr.module_weight, num_parts)  # 0.2 ???
    partMgr = FMPartMgr(hgr, gainMgr, constrMgr)
    partMgr.legalize(part)  # ???
    totalcostbefore = partMgr.totalcost
    partMgr.init(part)
    assert partMgr.totalcost == totalcostbefore
    partMgr.optimize(part)
    assert partMgr.totalcost <= totalcostbefore
    totalcostbefore = partMgr.totalcost
    partMgr.init(part)
    assert partMgr.totalcost == totalcostbefore
    # print(partMgr.snapshot)


def test_FMKWayPartMgr():
    hgr = create_drawf()
    gainMgr = FMKWayGainMgr(FMKWayGainCalc, hgr, 3)
    hgr.module_fixed = {"p1"}
    part = {v: 0 for v in hgr}
    run_FMKWayPartMgr(hgr, gainMgr, 3, part)


def test_FMKWayPartMgr2():
    hgr = create_test_netlist()
    gainMgr = FMKWayGainMgr(FMKWayGainCalc, hgr, 3)
    part = {v: 0 for v in hgr}
    run_FMKWayPartMgr(hgr, gainMgr, 3, part)


def test_FMKWayPartMgr3():
    hgr = create_random_hgraph()
    gainMgr = FMKWayGainMgr(FMKWayGainCalc, hgr, 3)
    part = [0 for _ in hgr]
    run_FMKWayPartMgr(hgr, gainMgr, 3, part)


def test_FMKWayPartMgr4():
    hgr = read_json("testcases/p1.json")
    gainMgr = FMKWayGainMgr(FMKWayGainCalc, hgr, 3)
    part = [0 for _ in hgr]
    run_FMKWayPartMgr(hgr, gainMgr, 3, part)


# if __name__ == "__main__":
#     test_FMKWayPartMgr2()
