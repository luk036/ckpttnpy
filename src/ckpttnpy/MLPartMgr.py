"""Multi-level FM partitioning manager.

MLPartMgr implements multi-level recursive partitioning: contracts large hypergraphs
into smaller ones, recurses, then uncoarsens with FM optimization at each level.
Provides MLBiPartMgr (2-way) and MLKWayPartMgr (k-way) specializations.
"""

import gc
from typing import Any

from .FMConstrMgr import LegalCheck
from .FMPartSpec import BI_FM, BI_NN, KWAY_FM, KWAY_NN, FMPartSpec

# Take a snapshot when a move make **negative** gain.
# Snapshot in the form of "interface"???
from .min_cover import contract_subgraph


class MLPartMgr:
    """The `MLPartMgr` class is a manager for Multi-level Partitioning."""

    def __init__(self, spec: FMPartSpec, bal_tol: float, num_parts: int = 2) -> None:
        self.spec = spec
        self.bal_tol = bal_tol
        self.num_parts = num_parts
        self.totalcost = 0
        self.LIMIT_SIZE = 50

    @property
    def limitsize(self) -> int:
        return self.LIMIT_SIZE

    @limitsize.setter
    def limitsize(self, limit: int) -> None:
        self.LIMIT_SIZE = limit

    def run_Partition(
        self, hyprgraph: Any, module_weight: Any, part: Any
    ) -> LegalCheck:
        def make_part_mgr() -> Any:
            return self.spec.make_part_mgr(
                hyprgraph, self.bal_tol, module_weight, self.num_parts
            )

        def legalcheck_fn() -> tuple[LegalCheck, int]:
            part_mgr = make_part_mgr()
            legalcheck = part_mgr.legalize(part)
            return legalcheck, part_mgr.totalcost

        def optimize_fn() -> int:
            part_mgr = make_part_mgr()
            part_mgr.optimize(part)
            return part_mgr.totalcost  # type: ignore[no-any-return]

        legalcheck, totalcost = legalcheck_fn()
        if legalcheck != LegalCheck.AllSatisfied:
            self.totalcost = totalcost
            return legalcheck

        if hyprgraph.number_of_modules() >= self.limitsize:  # OK
            try:
                hgr2, module_weight2 = contract_subgraph(
                    hyprgraph, module_weight, set()
                )
                if hgr2.number_of_modules() * 3 / 2 < hyprgraph.number_of_modules():
                    part2 = [0] * hgr2.number_of_modules()
                    hgr2.projection_up(part, part2)
                    legalcheck_recur = self.run_Partition(hgr2, module_weight2, part2)
                    if legalcheck_recur == LegalCheck.AllSatisfied:
                        hgr2.projection_down(part2, part)
            except MemoryError:
                print("MemoryError: Not enough memory available.")
                gc.collect()

        self.totalcost = optimize_fn()
        assert self.totalcost >= 0
        return legalcheck


# The MLBiPartMgr class is a subclass of MLPartMgr that initializes with specific parameters for
# balancing tolerance.
class MLBiPartMgr(MLPartMgr):
    def __init__(self, bal_tol: float) -> None:
        MLPartMgr.__init__(self, BI_FM, bal_tol, 2)


class MLKWayPartMgr(MLPartMgr):
    def __init__(self, bal_tol: float, num_parts: int) -> None:
        MLPartMgr.__init__(self, KWAY_FM, bal_tol, num_parts)


# The MLBiPartMgr class is a subclass of MLPartMgr that initializes with specific parameters for
# balancing tolerance.
class MLBiNNPartMgr(MLPartMgr):
    def __init__(self, bal_tol: float) -> None:
        MLPartMgr.__init__(self, BI_NN, bal_tol, 2)


class MLKWayNNPartMgr(MLPartMgr):
    def __init__(self, bal_tol: float, num_parts: int) -> None:
        MLPartMgr.__init__(self, KWAY_NN, bal_tol, num_parts)
