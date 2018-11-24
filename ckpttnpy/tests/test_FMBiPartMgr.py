from ckpttnpy.FMBiGainMgr import FMBiGainMgr
from ckpttnpy.FMBiConstrMgr import FMBiConstrMgr
from ckpttnpy.FMBiPart import FMBiPartMgr
from ckpttnpy.tests.test_netlist import create_test_netlist

def test_FMBiPartMgr():
    H = create_test_netlist()
    gainMgr = FMBiGainMgr(H)
    constrMgr = FMBiConstrMgr(H, 0.7)
    assert H.G.nodes[0].get('weight', 1) == 5844

    partMgr = FMBiPartMgr(H, gainMgr, constrMgr)
    partMgr.init()
    totalcostbefore = partMgr.totalcost
    partMgr.optimize()
    assert partMgr.totalcost <= totalcostbefore
    print(partMgr.snapshot)

if __name__ == "__main__":
    test_FMBiPartMgr()