"""Tests for MLPartMgr using IBM-PLACE benchmark format netlists.

Reads ibm01.net and ibm01.are using netlistx.readwrite (ported
from netlistx-cpp/source/readwrite.cpp).
"""
from random import randint, seed

from netlistx.readwrite import read_are, read_netd

from ckpttnpy.FMBiConstrMgr import FMBiConstrMgr
from ckpttnpy.FMConstrMgr import LegalCheck
from ckpttnpy.FMKWayConstrMgr import FMKWayConstrMgr
from ckpttnpy.MLPartMgr import MLBiPartMgr, MLKWayPartMgr
from tests.mocks import Part


def _load_ibm01():
    """Load ibm01.net + ibm01.are into a Netlist.

    IBM01: 12752 modules (12505 cells + 247 pads), 14111 nets.
    """
    hyprgraph = read_netd("testcases/ibm01.net")
    read_are(hyprgraph, "testcases/ibm01.are")
    return hyprgraph


def _run_MLBiPartMgr_ibm(hyprgraph):
    bal_tol = 0.45
    part_mgr = MLBiPartMgr(bal_tol)
    part_mgr.limitsize = 10
    randseq = [randint(0, 1) for _ in hyprgraph]
    part: Part = {v: k for v, k in zip(hyprgraph.modules, randseq)}

    legal_check = part_mgr.run_Partition(hyprgraph, hyprgraph.module_weight, part)
    assert legal_check == LegalCheck.AllSatisfied

    constr_mgr = FMBiConstrMgr(hyprgraph, bal_tol, hyprgraph.module_weight, 2)
    assert constr_mgr.final_check(part)

    return part_mgr.totalcost


def _run_MLKWayPartMgr_ibm(hyprgraph, num_parts: int):
    bal_tol = 0.45
    part_mgr = MLKWayPartMgr(bal_tol, num_parts)
    part_mgr.limitsize = 10
    randseq = [randint(0, num_parts - 1) for _ in hyprgraph]
    part: Part = {v: k for v, k in zip(hyprgraph.modules, randseq)}

    legal_check = part_mgr.run_Partition(hyprgraph, hyprgraph.module_weight, part)
    assert legal_check == LegalCheck.AllSatisfied

    constr_mgr = FMKWayConstrMgr(hyprgraph, bal_tol, hyprgraph.module_weight, num_parts)
    assert constr_mgr.final_check(part)

    return part_mgr.totalcost


def test_ibm01_MLBiPartMgr() -> None:
    seed(42)
    hyprgraph = _load_ibm01()
    cost = _run_MLBiPartMgr_ibm(hyprgraph)
    assert cost >= 0


def test_ibm01_MLKWayPartMgr() -> None:
    seed(42)
    hyprgraph = _load_ibm01()
    cost = _run_MLKWayPartMgr_ibm(hyprgraph, 3)
    assert cost >= 0
