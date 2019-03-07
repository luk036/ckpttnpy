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


def run_MLBiPartMgr(H):
    partMgr = MLPartMgr(FMBiGainCalc, FMBiGainMgr,
                        FMBiConstrMgr, FMPartMgr, 0.4)
    part = list(0 for _ in H.modules)
    part_info = part, set()
    partMgr.run_FMPartition(H, part_info)
    return partMgr.totalcost


def test_MLBiPartMgr():
    H = create_drawf()
    totalcost = run_MLBiPartMgr(H)
    assert totalcost == 2


def test_MLBiPartMgr2():
    H = create_p1()
    totalcost = run_MLBiPartMgr(H)
    assert totalcost >= 55
    assert totalcost <= 70


def run_MLKWayPartMgr(H):
    partMgr = MLPartMgr(FMKWayGainCalc, FMKWayGainMgr,
                        FMKWayConstrMgr, FMPartMgr, 0.4, 3)
    part = list(0 for _ in H.modules)
    part_info = part, set()
    partMgr.run_FMPartition(H, part_info)
    return partMgr.totalcost


def test_MLKWayPartMgr():
    H = create_drawf()
    totalcost = run_MLKWayPartMgr(H)
    assert totalcost == 4


def test_MLKWayPartMgr2():
    H = create_p1()
    totalcost = run_MLKWayPartMgr(H)
    assert totalcost >= 109
    assert totalcost <= 152


# if __name__ == "__main__":
#     test_MLKWayPartMgr()
