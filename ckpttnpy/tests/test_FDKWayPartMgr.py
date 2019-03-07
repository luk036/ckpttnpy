from ckpttnpy.FDKWayGainMgr import FDKWayGainMgr
from ckpttnpy.FDKWayGainCalc import FDKWayGainCalc
from ckpttnpy.FMKWayConstrMgr import FMKWayConstrMgr
from ckpttnpy.FDPartMgr import FDPartMgr
from ckpttnpy.tests.test_netlist import create_drawf, create_p1


def run_FDKWayPartMgr(H, gainMgr, K):
    """[summary]

    Arguments:
        H {Netlist} -- [description]
        gainMgr {gainMgr} -- [description]
        K {int} -- number of partitions
    """
    constrMgr = FMKWayConstrMgr(H, 0.4, K)  # 0.3 ???
    partMgr = FDPartMgr(H, gainMgr, constrMgr)
    part = list(0 for _ in H.modules)
    extern_nets = set()
    part_info = part, extern_nets
    # partMgr.init(part)
    partMgr.legalize(part_info)  # ???
    totalcostbefore = partMgr.totalcost
    partMgr.init(part_info)
    assert partMgr.totalcost == totalcostbefore
    partMgr.optimize(part_info)
    assert partMgr.totalcost <= totalcostbefore
    # print(partMgr.snapshot)


def test_FDKWayPartMgr2():
    H = create_drawf()
    gainMgr = FDKWayGainMgr(FDKWayGainCalc, H, 3)
    H.module_fixed = ['p1']
    run_FDKWayPartMgr(H, gainMgr, 3)


def test_FDKWayPartMgr3():
    H = create_p1()
    gainMgr = FDKWayGainMgr(FDKWayGainCalc, H, 3)
    run_FDKWayPartMgr(H, gainMgr, 3)


if __name__ == "__main__":
    test_FDKWayPartMgr2()
