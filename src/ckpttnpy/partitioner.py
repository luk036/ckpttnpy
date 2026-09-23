"""Factory helpers that select a partitioning algorithm family.

``resolve_spec`` is the single place that maps ``(k, algo)`` to a product
family. ``create_partitioner`` builds a multi-level manager on top of it;
``create_flat_part_mgr`` builds the single-level equivalent.
"""

from typing import Any

from .FMPartSpec import BI_FM, BI_NN, KWAY_FM, KWAY_NN, FMPartSpec
from .MLPartMgr import MLPartMgr
from .PartMgrBase import PartMgrBase


def resolve_spec(k: int, algo: str) -> FMPartSpec:
    """Return the product family for *k* partitions and algorithm *algo*."""
    if k < 2:
        raise ValueError(f"k must be >= 2, got {k}")
    if algo == "FM":
        return BI_FM if k == 2 else KWAY_FM
    if algo == "NN":
        return BI_NN if k == 2 else KWAY_NN
    raise ValueError(f"algo must be 'FM' or 'NN', got {algo!r}")


def create_partitioner(
    k: int, algo: str, bal_tol: float, limitsize: int = 50
) -> MLPartMgr:
    """Build a multi-level partitioner (coarsen, recurse, then refine)."""
    mgr = MLPartMgr(resolve_spec(k, algo), bal_tol, k)
    mgr.limitsize = limitsize
    return mgr


def create_flat_part_mgr(
    k: int, algo: str, bal_tol: float, hyprgraph: Any, module_weight: Any
) -> PartMgrBase:
    """Build a single-level partition manager (no coarsening)."""
    return resolve_spec(k, algo).make_part_mgr(hyprgraph, bal_tol, module_weight, k)
