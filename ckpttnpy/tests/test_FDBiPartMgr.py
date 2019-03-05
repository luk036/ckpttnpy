from ckpttnpy.FDBiGainMgr import FDBiGainMgr
from ckpttnpy.FDBiGainCalc import FDBiGainCalc
from ckpttnpy.FMBiConstrMgr import FMBiConstrMgr
from ckpttnpy.FDPartMgr import FDPartMgr
from ckpttnpy.tests.test_netlist import create_test_netlist, create_drawf, create_p1


def run_FDBiPartMgr(H):
    gainMgr = FDBiGainMgr(FDBiGainCalc, H)
    constrMgr = FMBiConstrMgr(H, 0.4)
    partMgr = FDPartMgr(H, gainMgr, constrMgr)
    part = list(0 for _ in H.modules)
    extern_nets = set()
    part_info = part, extern_nets
    # partMgr.init(part)
    partMgr.legalize(part_info)
    totalcostbefore = partMgr.totalcost
    partMgr.optimize(part_info)
    assert partMgr.totalcost <= totalcostbefore
    # print(partMgr.snapshot)


def test_FDBiPartMgr():
    H = create_test_netlist()
    run_FDBiPartMgr(H)


def test_FDBiPartMgr2():
    H = create_drawf()
    H.module_fixed = ['p1']
    run_FDBiPartMgr(H)


def test_FDBiPartMgr3():
    H = create_p1()
    run_FDBiPartMgr(H)


if __name__ == "__main__":
    test_FDBiPartMgr3()
