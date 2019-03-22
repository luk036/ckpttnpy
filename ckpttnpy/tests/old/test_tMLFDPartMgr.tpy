from ckpttnpy.MLPartMgr import MLPartMgr
from ckpttnpy.FDPartMgr import FDPartMgr
from ckpttnpy.FDBiGainCalc import FDBiGainCalc
from ckpttnpy.FDBiGainMgr import FDBiGainMgr
from ckpttnpy.FMBiConstrMgr import FMBiConstrMgr
from ckpttnpy.FDKWayGainCalc import FDKWayGainCalc
from ckpttnpy.FDKWayGainMgr import FDKWayGainMgr
from ckpttnpy.FMKWayConstrMgr import FMKWayConstrMgr
from ckpttnpy.tests.test_netlist import create_drawf, create_p1


def run_MLBiPartMgr(H):
    partMgr = MLPartMgr(FDBiGainCalc, FDBiGainMgr,
                        FMBiConstrMgr, FDPartMgr, 0.4)
    part = list(0 for _ in H.modules)
    extern_nets = set()
    part_info = part, extern_nets
    partMgr.run_Partition(H, part_info)
    return partMgr.totalcost


def test_MLBiPartMgr():
    H = create_drawf()
    totalcost = run_MLBiPartMgr(H)
    assert totalcost == 2


def test_MLBiPartMgr2():
    H = create_p1()
    totalcost = run_MLBiPartMgr(H)
    assert totalcost >= 49
    assert totalcost <= 87


def run_MLKWayPartMgr(H):
    partMgr = MLPartMgr(FDKWayGainCalc, FDKWayGainMgr,
                        FMKWayConstrMgr, FDPartMgr, 0.4, 3)
    part = list(0 for _ in H.modules)
    extern_nets = set()
    part_info = part, extern_nets
    partMgr.run_Partition(H, part_info)
    return partMgr.totalcost


def test_MLKWayPartMgr():
    H = create_drawf()
    totalcost = run_MLKWayPartMgr(H)
    assert totalcost == 4


def test_MLKWayPartMgr2():
    H = create_p1()
    totalcost = run_MLKWayPartMgr(H)
    assert totalcost >= 173
    assert totalcost <= 234


# if __name__ == "__main__":
#     test_MLBiPartMgr()
