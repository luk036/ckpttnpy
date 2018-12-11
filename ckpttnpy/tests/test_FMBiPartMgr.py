from ckpttnpy.FMBiGainMgr2 import FMBiGainMgr2
from ckpttnpy.FMBiGainCalc import FMBiGainCalc
from ckpttnpy.FMBiConstrMgr import FMBiConstrMgr
from ckpttnpy.FMPartMgr import FMPartMgr
from ckpttnpy.tests.test_netlist import create_test_netlist, create_drawf


def run_FMBiPartMgr(H):
    gainCalc = FMBiGainCalc(H)
    gainMgr = FMBiGainMgr2(H, gainCalc)
    constrMgr = FMBiConstrMgr(H, 0.3)
    partMgr = FMPartMgr(H, gainMgr, constrMgr)
    part = list(0 for _ in H.modules)
    partMgr.init(part)
    partMgr.legalize(part)
    totalcostbefore = partMgr.totalcost
    partMgr.optimize(part)
    assert partMgr.totalcost <= totalcostbefore
    print(partMgr.snapshot)


def test_FMBiPartMgr():
    H = create_test_netlist()
    run_FMBiPartMgr(H)


def test_FMBiPartMgr2():
    H = create_drawf()
    run_FMBiPartMgr(H)
