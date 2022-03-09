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


def run_FMKWayPartMgr(hgr: Netlist, gain_mgr, num_parts, part: Part):
    """[summary]

    Arguments:
        hgr (Netlist):  description
        gain_mgr (gain_mgr):  description
        num_parts (int):  number of partitions
    """
    constr_mgr = FMKWayConstrMgr(hgr, 0.4, hgr.module_weight, num_parts)  # 0.2 ???
    part_mgr = FMPartMgr(hgr, gain_mgr, constr_mgr)
    part_mgr.legalize(part)  # ???
    totalcostbefore = part_mgr.totalcost
    part_mgr.init(part)
    assert part_mgr.totalcost == totalcostbefore
    part_mgr.optimize(part)
    assert part_mgr.totalcost <= totalcostbefore
    totalcostbefore = part_mgr.totalcost
    part_mgr.init(part)
    assert part_mgr.totalcost == totalcostbefore
    # print(part_mgr.snapshot)


def test_FMKWayPartMgr():
    hgr = create_drawf()
    gain_mgr = FMKWayGainMgr(FMKWayGainCalc, hgr, 3)
    hgr.module_fixed = {"p1"}
    part = {v: 0 for v in hgr}
    run_FMKWayPartMgr(hgr, gain_mgr, 3, part)


def test_FMKWayPartMgr2():
    hgr = create_test_netlist()
    gain_mgr = FMKWayGainMgr(FMKWayGainCalc, hgr, 3)
    part = {v: 0 for v in hgr}
    run_FMKWayPartMgr(hgr, gain_mgr, 3, part)


def test_FMKWayPartMgr3():
    hgr = create_random_hgraph()
    gain_mgr = FMKWayGainMgr(FMKWayGainCalc, hgr, 3)
    part = [0 for _ in hgr]
    run_FMKWayPartMgr(hgr, gain_mgr, 3, part)


def test_FMKWayPartMgr4():
    hgr = read_json("testcases/p1.json")
    gain_mgr = FMKWayGainMgr(FMKWayGainCalc, hgr, 3)
    part = [0 for _ in hgr]
    run_FMKWayPartMgr(hgr, gain_mgr, 3, part)


# if __name__ == "__main__":
#     test_FMKWayPartMgr2()
