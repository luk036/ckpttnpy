from ckpttnpy.MLPartMgr import MLPartMgr
from ckpttnpy.tests.test_netlist import create_drawf
# from ckpttnpy.min_cover import create_contraction_subgraph
# from ckpttnpy.FMPartMgr import FMPartMgr
from ckpttnpy.FMBiGainCalc import FMBiGainCalc
from ckpttnpy.FMBiGainMgr import FMBiGainMgr
from ckpttnpy.FMBiConstrMgr import FMBiConstrMgr
from ckpttnpy.FMKWayGainCalc import FMKWayGainCalc
from ckpttnpy.FMKWayGainMgr import FMKWayGainMgr
from ckpttnpy.FMKWayConstrMgr import FMKWayConstrMgr


def run_MLBiPartMgr(H):
    partMgr = MLPartMgr(FMBiGainCalc, FMBiGainMgr, FMBiConstrMgr, 0.4)
    part = list(0 for _ in H.modules)
    partMgr.run_Partition(H, part)
    assert partMgr.totalcost == 2


def test_MLBiPartMgr():
    H = create_drawf()
    run_MLBiPartMgr(H)


def run_MLKWayPartMgr(H):
    partMgr = MLPartMgr(FMKWayGainCalc, FMKWayGainMgr, FMKWayConstrMgr, 0.4, 3)
    part = list(0 for _ in H.modules)
    partMgr.run_Partition(H, part)
    assert partMgr.totalcost == 4


def test_MLKWayPartMgr():
    H = create_drawf()
    run_MLKWayPartMgr(H)


# if __name__ == "__main__":
#     test_MLKWayPartMgr()
