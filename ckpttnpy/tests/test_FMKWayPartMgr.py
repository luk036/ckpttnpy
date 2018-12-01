from ckpttnpy.FMKWayGainMgr import FMKWayGainMgr
from ckpttnpy.FMKWayGainCalc import FMKWayGainCalc
from ckpttnpy.FMKWayConstrMgr import FMKWayConstrMgr
from ckpttnpy.FMPartMgr import FMPartMgr
from ckpttnpy.tests.test_netlist import create_drawf


def run_FMKWayPartMgr(H, gainMgr, K):
    constrMgr = FMKWayConstrMgr(H, 0.45, K)
    partMgr = FMPartMgr(H, gainMgr, constrMgr)
    partMgr.init()
    totalcostbefore = partMgr.totalcost
    partMgr.optimize()
    assert partMgr.totalcost <= totalcostbefore
    print(partMgr.snapshot)


def test_FMKWayPartMgr2():
    H = create_drawf()
    gainCalc = FMKWayGainCalc(H, 3)
    gainMgr = FMKWayGainMgr(H, gainCalc, 3)
    run_FMKWayPartMgr(H, gainMgr, 3)
