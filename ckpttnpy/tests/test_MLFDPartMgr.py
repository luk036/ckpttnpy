from ckpttnpy.MLPartMgr import MLPartMgr
from ckpttnpy.tests.test_netlist import create_drawf
# from ckpttnpy.min_cover import create_contraction_subgraph
from ckpttnpy.FDPartMgr import FDPartMgr
from ckpttnpy.FDBiGainCalc import FDBiGainCalc
from ckpttnpy.FDBiGainMgr import FDBiGainMgr
from ckpttnpy.FMBiConstrMgr import FMBiConstrMgr
from ckpttnpy.FDKWayGainCalc import FDKWayGainCalc
from ckpttnpy.FDKWayGainMgr import FDKWayGainMgr
from ckpttnpy.FMKWayConstrMgr import FMKWayConstrMgr


def run_MLBiPartMgr(H):
    partMgr = MLPartMgr(FDBiGainCalc, FDBiGainMgr, FMBiConstrMgr, FDPartMgr, 0.4)
    part = list(0 for _ in H.modules)
    extern_nets = set()
    part_info = part, extern_nets
    partMgr.run_Partition(H, part_info)
    assert partMgr.totalcost == 2


def test_MLBiPartMgr():
    H = create_drawf()
    run_MLBiPartMgr(H)


def run_MLKWayPartMgr(H):
    partMgr = MLPartMgr(FDKWayGainCalc, FDKWayGainMgr, FMKWayConstrMgr, FDPartMgr, 0.4, 3)
    part = list(0 for _ in H.modules)
    extern_nets = set()
    part_info = part, extern_nets
    partMgr.run_Partition(H, part_info)
    assert partMgr.totalcost == 4


def test_MLKWayPartMgr():
    H = create_drawf()
    run_MLKWayPartMgr(H)


# if __name__ == "__main__":
#     test_MLBiPartMgr()
