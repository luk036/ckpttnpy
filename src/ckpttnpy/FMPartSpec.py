"""Abstract Factory for the partitioning product families.

``FMPartSpec`` names the four collaborating classes that make up one algorithm
family (gain calculator, gain manager, constraint manager, partition manager)
and builds a partition manager from them. The four presets below are the single
definition of {bi, k-way} x {FM, NN} used across the project.
"""

from dataclasses import dataclass
from typing import Any, Type

from .FMBiConstrMgr import FMBiConstrMgr
from .FMBiGainCalc import FMBiGainCalc
from .FMBiGainMgr import FMBiGainMgr
from .FMKWayConstrMgr import FMKWayConstrMgr
from .FMKWayGainCalc import FMKWayGainCalc
from .FMKWayGainMgr import FMKWayGainMgr
from .FMPartMgr import FMPartMgr
from .NNPartMgr import NNPartMgr
from .PartMgrBase import PartMgrBase


@dataclass(frozen=True)
class FMPartSpec:
    """One FM/NN product family: the four classes that vary together."""

    GainCalc: Type
    GainMgr: Type
    ConstrMgr: Type
    PartMgr: Type[PartMgrBase]

    def make_part_mgr(
        self, hyprgraph: Any, bal_tol: float, module_weight: Any, num_parts: int
    ) -> PartMgrBase:
        """Wire up the family into a ready-to-run partition manager."""
        gain_mgr = self.GainMgr(self.GainCalc, hyprgraph, num_parts)
        constr_mgr = self.ConstrMgr(hyprgraph, bal_tol, module_weight, num_parts)
        return self.PartMgr(hyprgraph, gain_mgr, constr_mgr)


BI_FM = FMPartSpec(FMBiGainCalc, FMBiGainMgr, FMBiConstrMgr, FMPartMgr)
KWAY_FM = FMPartSpec(FMKWayGainCalc, FMKWayGainMgr, FMKWayConstrMgr, FMPartMgr)
BI_NN = FMPartSpec(FMBiGainCalc, FMBiGainMgr, FMBiConstrMgr, NNPartMgr)
KWAY_NN = FMPartSpec(FMKWayGainCalc, FMKWayGainMgr, FMKWayConstrMgr, NNPartMgr)
