from ckpttnpy.netlist import Netlist
from ckpttnpy.FMBiGainMgr import FMBiGainMgr
from ckpttnpy.tests.test_netlist import create_test_netlist


def test_FMBiGainMgr():
    H = create_test_netlist()
    mgr = FMBiGainMgr(H)
    part = [0, 1, 0]
    mgr.init(part)
    gain_before = mgr.gainbucket.get_key(mgr.vertex_list[0])
    assert gain_before == 1
    assert part == [0, 1, 0]
    for v in H.cell_list:
        mgr.update_move(part, v)
    # mgr.update_move(part, H.cell_list[0])
    # gain_after = mgr.gainbucket.get_key(mgr.vertex_list[0])
    # assert gain_after == -1
    # mgr.update_move(part, H.cell_list[0])
    gain_after = mgr.gainbucket.get_key(mgr.vertex_list[0])
    assert part == [1, 0, 1]
    assert gain_after == gain_before

if __name__ == "__main__":
    test_FMBiGainMgr()

