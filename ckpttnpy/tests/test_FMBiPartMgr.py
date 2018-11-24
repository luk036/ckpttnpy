from ckpttnpy.FMBiGainMgr import FMBiGainMgr
from ckpttnpy.FMBiGainMgr2 import FMBiGainMgr2
from ckpttnpy.FMBiConstrMgr import FMBiConstrMgr
from ckpttnpy.FMBiPart import FMBiPartMgr
from ckpttnpy.tests.test_netlist import create_test_netlist, create_drawf


def run_FMBiPartMgr(H, gainMgr):
    constrMgr = FMBiConstrMgr(H, 0.7)
    partMgr = FMBiPartMgr(H, gainMgr, constrMgr)
    partMgr.init()
    totalcostbefore = partMgr.totalcost
    partMgr.optimize()
    assert partMgr.totalcost <= totalcostbefore
    print(partMgr.snapshot)


def test_FMBiPartMgr():
    H = create_test_netlist()
    gainMgr = FMBiGainMgr(H)
    run_FMBiPartMgr(H, gainMgr)


def test_FMBiPartMgr2():
    H = create_drawf()
    gainMgr = FMBiGainMgr2(H)
    run_FMBiPartMgr(H, gainMgr)
