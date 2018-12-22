from ckpttnpy.MLPartMgr import MLPartMgr
from ckpttnpy.tests.test_netlist import create_drawf
# from ckpttnpy.min_cover import create_contraction_subgraph
# from ckpttnpy.FMPartMgr import FMPartMgr
# from ckpttnpy.FMBiGainMgr import FMBiGainMgr
# from ckpttnpy.FMBiGainCalc import FMBiGainCalc
# from ckpttnpy.FMBiConstrMgr import FMBiConstrMgr


def run_MLBiPartMgr(H):
    partMgr = MLPartMgr(0.2)
    part = list(0 for _ in H.modules)
    partMgr.run_BiPartition(H, part)
    assert partMgr.totalcost == 2


def test_MLBiPartMgr():
    H = create_drawf()
    run_MLBiPartMgr(H)


def run_MLKWayPartMgr(H):
    partMgr = MLPartMgr(0.3, 3)
    part = list(0 for _ in H.modules)
    partMgr.run_KWayPartition(H, part)
    assert partMgr.totalcost == 4


def test_MLKWayPartMgr():
    H = create_drawf()
    run_MLKWayPartMgr(H)


# if __name__ == "__main__":
#     test_MLKWayPartMgr()
