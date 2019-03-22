from ckpttnpy.FMBiGainMgr import FMBiGainMgr
from ckpttnpy.FMBiGainCalc import FMBiGainCalc
from ckpttnpy.tests.test_netlist import create_test_netlist, create_drawf


def run_FMBiGainMgr(H, part_info):
    mgr = FMBiGainMgr(FMBiGainCalc, H)
    mgr.init(part_info)
    part, _ = part_info
    while not mgr.is_empty():
        # Take the gainmax with v from gainbucket
        move_info_v, gainmax = mgr.select(part)
        if gainmax <= 0:
            continue
        mgr.update_move(part_info, move_info_v)
        mgr.update_move_v(move_info_v, gainmax)
        _, toPart, i_v = move_info_v
        part[i_v] = toPart
        assert i_v >= 0


def test_FMBiGainMgr():
    H = create_test_netlist()
    part = [0, 1, 0]
    part_info = part, set()
    run_FMBiGainMgr(H, part_info)


def test_FMBiGainMgr2():
    H = create_drawf()
    part = [0, 0, 0, 0, 1, 1, 1]
    part_info = part, set()
    run_FMBiGainMgr(H, part_info)
