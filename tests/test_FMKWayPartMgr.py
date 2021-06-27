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
    read_json
)

Part = Union[Dict[Any, int], List[int]]


def run_FMKWayPartMgr(H: Netlist, gainMgr, K, part: Part):
    """[summary]

    Arguments:
        H (Netlist):  description
        gainMgr (gainMgr):  description
        K (int):  number of partitions
    """
    constrMgr = FMKWayConstrMgr(H, 0.4, H.module_weight, K)  # 0.2 ???
    partMgr = FMPartMgr(H, gainMgr, constrMgr)
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
    H = create_drawf()
    gainMgr = FMKWayGainMgr(FMKWayGainCalc, H, 3)
    H.module_fixed = {'p1'}
    part = {v: 0 for v in H}
    run_FMKWayPartMgr(H, gainMgr, 3, part)


def test_FMKWayPartMgr2():
    H = create_test_netlist()
    gainMgr = FMKWayGainMgr(FMKWayGainCalc, H, 3)
    part = {v: 0 for v in H}
    run_FMKWayPartMgr(H, gainMgr, 3, part)


def test_FMKWayPartMgr3():
    H = create_random_hgraph()
    gainMgr = FMKWayGainMgr(FMKWayGainCalc, H, 3)
    part = [0 for _ in H]
    run_FMKWayPartMgr(H, gainMgr, 3, part)


def test_FMKWayPartMgr4():
    H = read_json('testcases/p1.json')
    gainMgr = FMKWayGainMgr(FMKWayGainCalc, H, 3)
    part = [0 for _ in H]
    run_FMKWayPartMgr(H, gainMgr, 3, part)

# if __name__ == "__main__":
#     test_FMKWayPartMgr2()
