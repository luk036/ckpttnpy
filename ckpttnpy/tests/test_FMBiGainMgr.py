from ckpttnpy.FMBiGainMgr import FMBiGainMgr
from ckpttnpy.FMBiGainMgr2 import FMBiGainMgr2
from ckpttnpy.tests.test_netlist import create_test_netlist, create_drawf


def run_FMBiGainMgr(H, part, mgr):
    mgr.init(part)
    while not mgr.is_empty():
        # Take the gainmax with v from gainbucket
        v, gainmax = mgr.select()
        if gainmax <= 0:
            continue
        fromPart = part[v]
        mgr.update_move(part, fromPart, v, gainmax)
        part[v] = 1 - fromPart
        assert v >= 0


def test_FMBiGainMgr():
    H = create_test_netlist()
    part = [0, 1, 0]
    mgr = FMBiGainMgr(H)
    run_FMBiGainMgr(H, part, mgr)


def test_FMBiGainMgr2():
    H = create_drawf()
    part = [0, 0, 0, 0, 1, 1, 1]
    mgr = FMBiGainMgr2(H)
    run_FMBiGainMgr(H, part, mgr)
