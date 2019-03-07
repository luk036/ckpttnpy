from ckpttnpy.FDBiGainMgr import FDBiGainMgr
from ckpttnpy.FMBiGainCalc import FMBiGainCalc
from ckpttnpy.FMBiConstrMgr import FMBiConstrMgr
from ckpttnpy.FMPartMgr import FMPartMgr
from ckpttnpy.tests.test_netlist import create_test_netlist, create_drawf, create_p1


def run_FMBiPartMgr(H):
    gainMgr = FDBiGainMgr(FMBiGainCalc, H)
    constrMgr = FMBiConstrMgr(H, 0.3)
    partMgr = FMPartMgr(H, gainMgr, constrMgr)
    part = list(0 for _ in H.modules)
    part_info = part, set()
    # partMgr.init(part)
    partMgr.legalize(part_info)
    totalcostbefore = partMgr.totalcost
    partMgr.optimize(part_info)
    assert partMgr.totalcost <= totalcostbefore
    # print(partMgr.snapshot)


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
