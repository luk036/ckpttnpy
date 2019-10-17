from ckpttnpy.FMBiGainCalc import FMBiGainCalc
from ckpttnpy.FMBiGainMgr import FMBiGainMgr
from ckpttnpy.netlist import create_drawf, create_test_netlist


def run_FMBiGainMgr(H, part):
    mgr = FMBiGainMgr(FMBiGainCalc, H)
    mgr.init(part)
    while not mgr.is_empty():
        # Take the gainmax with v from gainbucket
        move_info_v, gainmax = mgr.select(part)
        if gainmax <= 0:
            continue
        mgr.update_move(part, move_info_v)
        mgr.update_move_v(move_info_v, gainmax)
        _, toPart, v = move_info_v
        part[v] = toPart
        # assert v >= 0


def test_FMBiGainMgr():
    H = create_test_netlist()
    part = {v: 0 for v in H.modules}
    part['a1'] = 1
    run_FMBiGainMgr(H, part)


def test_FMBiGainMgr2():
    H = create_drawf()
    part = {v: 0 for v in H.modules}
    part['a1'] = 1
    run_FMBiGainMgr(H, part)
