from ckpttnpy.FMKWayGainMgr import FMKWayGainMgr
from ckpttnpy.FMKWayConstrMgr import FMKWayConstrMgr
from ckpttnpy.FMKWayPart import FMKWayPartMgr
from ckpttnpy.tests.test_netlist import create_test_netlist, create_drawf


def run_FMKWayPartMgr(H, K, gainMgr):
    constrMgr = FMKWayConstrMgr(H, K, 0.7)
    partMgr = FMKWayPartMgr(H, K, gainMgr, constrMgr)
    partMgr.init()
    totalcostbefore = partMgr.totalcost
    partMgr.optimize()
    assert partMgr.totalcost <= totalcostbefore
    print(partMgr.snapshot)


def test_FMKWayPartMgr2():
    H = create_drawf()
    gainMgr = FMKWayGainMgr(H, 3)
    run_FMKWayPartMgr(H, 3, gainMgr)
