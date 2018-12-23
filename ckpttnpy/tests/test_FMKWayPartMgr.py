from ckpttnpy.FMKWayGainMgr import FMKWayGainMgr
from ckpttnpy.FMKWayGainCalc import FMKWayGainCalc
from ckpttnpy.FMKWayConstrMgr import FMKWayConstrMgr
from ckpttnpy.FMPartMgr import FMPartMgr
from ckpttnpy.tests.test_netlist import create_drawf


def run_FMKWayPartMgr(H, gainMgr, K):
    """[summary]

    Arguments:
        H {Netlist} -- [description]
        gainMgr {gainMgr} -- [description]
        K {int} -- number of partitions
    """
    constrMgr = FMKWayConstrMgr(H, 0.4, K)  # 0.2 ???
    partMgr = FMPartMgr(H, gainMgr, constrMgr)
    part = list(0 for _ in H.modules)
    partMgr.init(part)
    partMgr.legalize(part)  # ???
    totalcostbefore = partMgr.totalcost
    partMgr.init(part)
    assert partMgr.totalcost == totalcostbefore
    partMgr.optimize(part)
    assert partMgr.totalcost <= totalcostbefore
    # print(partMgr.snapshot)


def test_FMKWayPartMgr2():
    H = create_drawf()
    gainMgr = FMKWayGainMgr(FMKWayGainCalc, H, 3)
    H.module_fixed = [3]
    run_FMKWayPartMgr(H, gainMgr, 3)


if __name__ == "__main__":
    test_FMKWayPartMgr2()
