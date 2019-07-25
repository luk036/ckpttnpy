from ckpttnpy.FMBiConstrMgr import FMBiConstrMgr
from ckpttnpy.FMBiGainCalc import FMBiGainCalc
from ckpttnpy.FMBiGainMgr import FMBiGainMgr
from ckpttnpy.FMPartMgr import FMPartMgr
from ckpttnpy.netlist import create_drawf, create_p1, create_test_netlist


def run_FMBiPartMgr(H):
    gainMgr = FMBiGainMgr(FMBiGainCalc, H)
    constrMgr = FMBiConstrMgr(H, 0.3)
    partMgr = FMPartMgr(H, gainMgr, constrMgr)
    part = list(0 for _ in H.modules)
    partMgr.legalize(part)
    totalcostbefore = partMgr.totalcost
    partMgr.optimize(part)
    assert partMgr.totalcost <= totalcostbefore


def test_FMBiPartMgr():
    H = create_test_netlist()
    run_FMBiPartMgr(H)


def test_FMBiPartMgr2():
    H = create_drawf()
    H.module_fixed = ['p1']
    run_FMBiPartMgr(H)


def test_FMBiPartMgr3():
    H = create_p1()
    run_FMBiPartMgr(H)
