from ckpttnpy.MLPartMgr import MLPartMgr
from ckpttnpy.tests.test_netlist import create_drawf, create_p1
# from ckpttnpy.min_cover import create_contraction_subgraph
from ckpttnpy.FMPartMgr import FMPartMgr
from ckpttnpy.FMBiGainCalc import FMBiGainCalc
from ckpttnpy.FMBiGainMgr import FMBiGainMgr
from ckpttnpy.FMBiConstrMgr import FMBiConstrMgr
from ckpttnpy.FMKWayGainCalc import FMKWayGainCalc
from ckpttnpy.FMKWayGainMgr import FMKWayGainMgr
from ckpttnpy.FMKWayConstrMgr import FMKWayConstrMgr
from numpy.random import randint


def run_MLBiPartMgr(H):
    partMgr = MLPartMgr(FMBiGainCalc, FMBiGainMgr,
                        FMBiConstrMgr, FMPartMgr, 0.4)
    mincost = 1000
    for _ in range(10):
        # part = list(0 for _ in H.modules)
        randseq = randint(2, size=H.number_of_modules())
        part = list(randseq)
        # part_info = part, set()
        partMgr.run_FMPartition(H, part)
        if mincost > partMgr.totalcost:
            mincost = partMgr.totalcost
    return mincost


def test_MLBiPartMgr():
    H = create_drawf()
    totalcost = run_MLBiPartMgr(H)
    # assert totalcost == 2 # ???


def test_MLBiPartMgr2():
    H = create_p1()
    totalcost = run_MLBiPartMgr(H)
    # assert totalcost >= 55
    # assert totalcost <= 70
    assert totalcost >= 43
    assert totalcost <= 64


def run_MLKWayPartMgr(H, K):
    partMgr = MLPartMgr(FMKWayGainCalc, FMKWayGainMgr,
                        FMKWayConstrMgr, FMPartMgr, 0.4, K)
    mincost = 1000
    for _ in range(10):
        # part = list(0 for _ in H.modules)
        randseq = randint(K, size=H.number_of_modules())
        part = list(randseq)
        # part_info = part, set()
        partMgr.run_FMPartition(H, part)
        if mincost > partMgr.totalcost:
            mincost = partMgr.totalcost
    return mincost


def test_MLKWayPartMgr():
    H = create_drawf()
    totalcost = run_MLKWayPartMgr(H, 3)
    # assert totalcost == 4 # ???


def test_MLKWayPartMgr2():
    H = create_p1()
    totalcost = run_MLKWayPartMgr(H, 3)
    # assert totalcost >= 109
    # assert totalcost <= 152
    assert totalcost >= 77
    assert totalcost <= 119


# if __name__ == "__main__":
#     test_MLKWayPartMgr()
