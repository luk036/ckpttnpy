"""Tests for MLPartMgr using Yosys-generated netlist JSON files.

These tests validate that the multi-level partitioning manager correctly
handles netlists created from Yosys synthesis output (see yosys_testcases/).
Yosys netlists differ from standard test netlists in that:
- Modules are always a list (never a range)
- Module weights are stored as a dict (cells=1, ports=0)
- Port nodes are marked as fixed in module_fixed set
"""
from random import randint, seed

from netlistx.netlist import read_yosys_json

from ckpttnpy.FMBiConstrMgr import FMBiConstrMgr
from ckpttnpy.FMConstrMgr import LegalCheck
from ckpttnpy.FMKWayConstrMgr import FMKWayConstrMgr
from ckpttnpy.MLPartMgr import MLBiPartMgr, MLKWayPartMgr
from tests.mocks import Part


def _run_MLBiPartMgr_yosys(hyprgraph):
    """Run bipartitioning on a Yosys-derived netlist and verify legality.

    Args:
        hyprgraph: Netlist from read_yosys_json()

    Returns:
        Total cost of the partitioning.
    """
    bal_tol = 0.4
    part_mgr = MLBiPartMgr(bal_tol)
    part_mgr.limitsize = 7
    randseq = [randint(0, 1) for _ in hyprgraph]

    # Yosys netlists always use list-based modules → dict part
    part: Part = {v: k for v, k in zip(hyprgraph.modules, randseq)}

    legal_check = part_mgr.run_Partition(hyprgraph, hyprgraph.module_weight, part)
    assert legal_check == LegalCheck.AllSatisfied

    constr_mgr = FMBiConstrMgr(hyprgraph, bal_tol, hyprgraph.module_weight, 2)
    assert constr_mgr.final_check(part)

    return part_mgr.totalcost


def _run_MLKWayPartMgr_yosys(hyprgraph, num_parts: int):
    """Run k-way partitioning on a Yosys-derived netlist and verify legality.

    Args:
        hyprgraph: Netlist from read_yosys_json()
        num_parts: Number of partitions (k)

    Returns:
        Total cost of the partitioning.
    """
    bal_tol = 0.4
    part_mgr = MLKWayPartMgr(bal_tol, num_parts)
    randseq = [randint(0, num_parts - 1) for _ in hyprgraph]

    # Yosys netlists always use list-based modules → dict part
    part: Part = {v: k for v, k in zip(hyprgraph.modules, randseq)}

    legal_check = part_mgr.run_Partition(hyprgraph, hyprgraph.module_weight, part)
    assert legal_check == LegalCheck.AllSatisfied

    constr_mgr = FMKWayConstrMgr(hyprgraph, bal_tol, hyprgraph.module_weight, num_parts)
    assert constr_mgr.final_check(part)

    return part_mgr.totalcost


# ---------------------------------------------------------------------------
# Tests with sphere_netlist.json (circle_fsm_32bit_simple_fixed)
# 56 cells + 9 ports = 65 modules, 623 nets
# ---------------------------------------------------------------------------


def test_yosys_sphere_MLBiPartMgr() -> None:
    """Bi-partition the sphere Yosys netlist."""
    seed(42)
    hyprgraph = read_yosys_json("yosys_testcases/sphere_netlist.json")
    cost = _run_MLBiPartMgr_yosys(hyprgraph)
    assert cost >= 0


def test_yosys_sphere_MLKWayPartMgr() -> None:
    """3-way partition the sphere Yosys netlist."""
    seed(42)
    hyprgraph = read_yosys_json("yosys_testcases/sphere_netlist.json")
    cost = _run_MLKWayPartMgr_yosys(hyprgraph, 3)
    assert cost >= 0


# ---------------------------------------------------------------------------
# Tests with sphere3hopf_netlist_simple.json (cordic_trig_16bit_simple_fixed)
# 180 cells + 8 ports = 188 modules, 2825 nets
# ---------------------------------------------------------------------------


def test_yosys_sphere3hopf_MLBiPartMgr() -> None:
    """Bi-partition the sphere3hopf Yosys netlist."""
    seed(42)
    hyprgraph = read_yosys_json("yosys_testcases/sphere3hopf_netlist_simple.json")
    cost = _run_MLBiPartMgr_yosys(hyprgraph)
    assert cost >= 0


def test_yosys_sphere3hopf_MLKWayPartMgr() -> None:
    """3-way partition the sphere3hopf Yosys netlist."""
    seed(42)
    hyprgraph = read_yosys_json("yosys_testcases/sphere3hopf_netlist_simple.json")
    cost = _run_MLKWayPartMgr_yosys(hyprgraph, 3)
    assert cost >= 0
