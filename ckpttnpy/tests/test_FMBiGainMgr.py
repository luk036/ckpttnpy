from ckpttnpy.FMBiGainMgr import FMBiGainMgr
from ckpttnpy.tests.test_netlist import create_test_netlist
from ckpttnpy.dllist import dllink


def test_FMBiGainMgr():
    H = create_test_netlist()
    mgr = FMBiGainMgr(H)
    part = [0, 1, 0]
    mgr.init(part)
    gain_before = mgr.gainbucket.get_key(mgr.vertex_list[2])
    max_before = mgr.gainbucket.get_max()
    # assert gain_before == 1
    assert part == [0, 1, 0]
    for v in H.cell_list:
        fromPart = part[v]
        mgr.update_move(part, fromPart, v)
        part[v] = 1 - fromPart
    gain_after = mgr.gainbucket.get_key(mgr.vertex_list[2])
    max_after = mgr.gainbucket.get_max()
    assert part == [1, 0, 1]
    assert gain_after == gain_before
    assert max_after == max_before

    waitinglist = dllink()
    while not mgr.gainbucket.is_empty():
        # Take the gainmax with v from gainbucket
        # gainmax = mgr.gainbucket.get_max()
        vlink = mgr.gainbucket.popleft()
        waitinglist.append(vlink)
        v = vlink.idx
        assert v >= 0
        assert v < 3
        # v = H.cell_list[i_v]

if __name__ == "__main__":
    test_FMBiGainMgr()

