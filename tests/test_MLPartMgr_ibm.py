"""Tests for MLPartMgr using IBM-PLACE benchmark format netlists.

Reads ibm01.net and ibm01.are using netlistx.readwrite (ported
from netlistx-cpp/source/readwrite.cpp).
"""
import random

from netlistx.readwrite import read_are, read_netd

from ckpttnpy.FMBiConstrMgr import FMBiConstrMgr
from ckpttnpy.FMConstrMgr import LegalCheck
from ckpttnpy.FMKWayConstrMgr import FMKWayConstrMgr
from ckpttnpy.harness import make_init_part
from ckpttnpy.MLPartMgr import MLBiPartMgr, MLKWayPartMgr


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
    part = make_init_part(hyprgraph, 2, random)

    legal_check = part_mgr.run_Partition(hyprgraph, hyprgraph.module_weight, part)
    assert legal_check == LegalCheck.AllSatisfied

    constr_mgr = FMBiConstrMgr(hyprgraph, bal_tol, hyprgraph.module_weight, 2)
    assert constr_mgr.final_check(part)

    return part_mgr.totalcost


def _run_MLKWayPartMgr_ibm(hyprgraph, num_parts: int):
    bal_tol = 0.45
    part_mgr = MLKWayPartMgr(bal_tol, num_parts)
    part_mgr.limitsize = 10
    part = make_init_part(hyprgraph, num_parts, random)

    legal_check = part_mgr.run_Partition(hyprgraph, hyprgraph.module_weight, part)
    assert legal_check == LegalCheck.AllSatisfied

    constr_mgr = FMKWayConstrMgr(hyprgraph, bal_tol, hyprgraph.module_weight, num_parts)
    assert constr_mgr.final_check(part)

    return part_mgr.totalcost


def test_ibm01_MLBiPartMgr() -> None:
    random.seed(42)
    hyprgraph = _load_ibm01()
    cost = _run_MLBiPartMgr_ibm(hyprgraph)
    assert cost >= 0


def test_ibm01_MLKWayPartMgr() -> None:
    random.seed(42)
    hyprgraph = _load_ibm01()
    cost = _run_MLKWayPartMgr_ibm(hyprgraph, 3)
    assert cost >= 0
