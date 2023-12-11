from typing import Any, Dict, List, Union

from ckpttnpy.FMBiGainCalc import FMBiGainCalc
from ckpttnpy.FMBiGainMgr import FMBiGainMgr
from netlistx.netlist import Netlist, create_drawf, create_test_netlist

Part = Union[Dict[Any, int], List[int]]


def run_FMBiGainMgr(hyprgraph: Netlist, part: Part):
    mgr = FMBiGainMgr(FMBiGainCalc, hyprgraph)
    mgr.init(part)
    while not mgr.is_empty():
        # Take the gainmax with v from gainbucket
        move_info_v, gainmax = mgr.select(part)
        if gainmax <= 0:
            continue
        mgr.update_move(part, move_info_v)
        mgr.update_move_v(move_info_v, gainmax)
        v, _, to_part = move_info_v
        part[v] = to_part
        # assert v >= 0


def test_FMBiGainMgr():
    hyprgraph = create_test_netlist()
    part = {v: 0 for v in hyprgraph}
    part["a1"] = 1
    run_FMBiGainMgr(hyprgraph, part)


def test_FMBiGainMgr2():
    hyprgraph = create_drawf()
    part = {v: 0 for v in hyprgraph}
    part["a1"] = 1
    run_FMBiGainMgr(hyprgraph, part)
