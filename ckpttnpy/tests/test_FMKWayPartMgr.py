from ckpttnpy.FMKWayGainMgr import FMKWayGainMgr
from ckpttnpy.FMKWayGainCalc import FMKWayGainCalc
from ckpttnpy.FMKWayConstrMgr import FMKWayConstrMgr
from ckpttnpy.FMPartMgr import FMPartMgr
from ckpttnpy.tests.test_netlist import create_drawf


def run_FMKWayPartMgr(H, gainMgr, K):
    constrMgr = FMKWayConstrMgr(H, 0.3, K) # 0.2 ???
    partMgr = FMPartMgr(H, gainMgr, constrMgr)
    part = list(0 for _ in H.modules)
    partMgr.init(part)
    partMgr.legalize(part) # ???
    # partMgr.init(part)
    totalcostbefore = partMgr.totalcost
    partMgr.optimize(part)
    assert partMgr.totalcost <= totalcostbefore
    # print(partMgr.snapshot)


def test_FMKWayPartMgr2():
    H = create_drawf()
    gainMgr = FMKWayGainMgr(FMKWayGainCalc, H, 3)
    H.module_fixed = [3]
    run_FMKWayPartMgr(H, gainMgr, 3)
