from typing import Any

import pytest
from netlistx.netlist import Netlist, create_drawf, create_test_netlist

from ckpttnpy.FMBiGainCalc import FMBiGainCalc
from ckpttnpy.FMBiGainMgr import FMBiGainMgr

from tests.mocks import Part


def _run_FMBiGainMgr(hyprgraph: Netlist, part: Part) -> None:
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


@pytest.mark.parametrize("create_netlist", [create_test_netlist, create_drawf])
def test_FMBiGainMgr(create_netlist: Any) -> None:
    hyprgraph = create_netlist()
    part = {v: 0 for v in hyprgraph}
    part["a1"] = 1
    _run_FMBiGainMgr(hyprgraph, part)
