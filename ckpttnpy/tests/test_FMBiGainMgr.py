from ckpttnpy.FMBiGainMgr2 import FMBiGainMgr2
from ckpttnpy.FMBiGainCalc import FMBiGainCalc
from ckpttnpy.tests.test_netlist import create_test_netlist, create_drawf


def run_FMBiGainMgr(H, part):
    gainCalc = FMBiGainCalc(H)
    mgr = FMBiGainMgr2(H, gainCalc)
    mgr.init(part)
    while not mgr.is_empty():
        # Take the gainmax with v from gainbucket
        move_info_v, gainmax = mgr.select(part)
        if gainmax <= 0:
            continue
        mgr.update_move(part, move_info_v)
        mgr.update_move_v(part, move_info_v, gainmax)
        _, toPart, v = move_info_v
        part[H.module_map[v]] = toPart
        assert v >= 0


def test_FMBiGainMgr():
    H = create_test_netlist()
    part = [0, 1, 0]
    run_FMBiGainMgr(H, part)


def test_FMBiGainMgr2():
    H = create_drawf()
    part = [0, 0, 0, 0, 1, 1, 1]
    run_FMBiGainMgr(H, part)
