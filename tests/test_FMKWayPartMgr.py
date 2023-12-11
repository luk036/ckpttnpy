from typing import Any, Dict, List, Union

from ckpttnpy.FMKWayConstrMgr import FMKWayConstrMgr
from ckpttnpy.FMKWayGainCalc import FMKWayGainCalc
from ckpttnpy.FMKWayGainMgr import FMKWayGainMgr
from ckpttnpy.FMPartMgr import FMPartMgr
from netlistx.netlist import (
    Netlist,
    create_drawf,
    create_random_hgraph,
    create_test_netlist,
    read_json,
)

Part = Union[Dict[Any, int], List[int]]


def run_FMKWayPartMgr(hyprgraph: Netlist, gain_mgr, num_parts, part: Part):
    """[summary]

    Arguments:
        hyprgraph (Netlist):  description
        gain_mgr (gain_mgr):  description
        num_parts (int):  number of partitions
    """
    constr_mgr = FMKWayConstrMgr(
        hyprgraph, 0.4, hyprgraph.module_weight, num_parts
    )  # 0.2 ???
    part_mgr = FMPartMgr(hyprgraph, gain_mgr, constr_mgr)
    part_mgr.legalize(part)  # TODO
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
    hyprgraph = create_drawf()
    gain_mgr = FMKWayGainMgr(FMKWayGainCalc, hyprgraph, 3)
    hyprgraph.module_fixed = {"p1"}
    part = {v: 0 for v in hyprgraph}
    run_FMKWayPartMgr(hyprgraph, gain_mgr, 3, part)


def test_FMKWayPartMgr2():
    hyprgraph = create_test_netlist()
    gain_mgr = FMKWayGainMgr(FMKWayGainCalc, hyprgraph, 3)
    part = {v: 0 for v in hyprgraph}
    run_FMKWayPartMgr(hyprgraph, gain_mgr, 3, part)


def test_FMKWayPartMgr3():
    hyprgraph = create_random_hgraph()
    gain_mgr = FMKWayGainMgr(FMKWayGainCalc, hyprgraph, 3)
    part = [0 for _ in hyprgraph]
    run_FMKWayPartMgr(hyprgraph, gain_mgr, 3, part)


def test_FMKWayPartMgr4():
    hyprgraph = read_json("testcases/p1.json")
    gain_mgr = FMKWayGainMgr(FMKWayGainCalc, hyprgraph, 5)
    part = [0 for _ in hyprgraph]
    run_FMKWayPartMgr(hyprgraph, gain_mgr, 5, part)


# if __name__ == "__main__":
#     test_FMKWayPartMgr2()
