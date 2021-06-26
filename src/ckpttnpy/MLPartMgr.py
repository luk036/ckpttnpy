# type: ignore

# from ckpttnpy.min_cover import create_contraction_subgraph
from ckpttnpy.FMPartMgr import FMPartMgr

# **Special code for two-pin nets**
from .FMBiConstrMgr import FMBiConstrMgr
from .FMBiGainCalc import FMBiGainCalc
from .FMBiGainMgr import FMBiGainMgr
from .FMConstrMgr import LegalCheck
from .FMKWayConstrMgr import FMKWayConstrMgr
from .FMKWayGainCalc import FMKWayGainCalc
from .FMKWayGainMgr import FMKWayGainMgr
# Take a snapshot when a move make **negative** gain.
# Snapshot in the form of "interface"???
from .min_cover import create_contraction_subgraph


class MLPartMgr:
    def __init__(self, GainCalc, GainMgr, ConstrMgr, PartMgr, BalTol, K=2):
        """[summary]

        Arguments:
            GainCalc (type):  description
            GainMgr (type):  description
            ConstrMgr (type):  description
            BalTol (type):  description

        Keyword Arguments:
            K (int):  description (default: {2})
        """
        self.GainCalc = GainCalc
        self.GainMgr = GainMgr
        self.ConstrMgr = ConstrMgr
        self.PartMgr = PartMgr
        self.BalTol = BalTol
        self.K = K
        self.totalcost = 0

    def run_FMPartition(self, H, module_weight, part, limitsize=7):
        """[summary]

        Arguments:
            H (type):  description
            part (type):  description

        Keyword Arguments:
            limitsize (int):  description (default: {7})

        Returns:
            dtype:  description
        """
        def legalcheck_fn():
            gainMgr = self.GainMgr(self.GainCalc, H, self.K)
            constrMgr = self.ConstrMgr(H, self.BalTol, module_weight, self.K)
            partMgr = self.PartMgr(H, gainMgr, constrMgr)
            return partMgr.legalize(part)

        def optimize_fn():
            gainMgr = self.GainMgr(self.GainCalc, H, self.K)
            constrMgr = self.ConstrMgr(H, self.BalTol, module_weight, self.K)
            partMgr = self.PartMgr(H, gainMgr, constrMgr)
            partMgr.optimize(part)
            return partMgr.totalcost

        legalcheck = legalcheck_fn();
        if legalcheck != LegalCheck.allsatisfied:
            return legalcheck

        if H.number_of_modules() >= limitsize:  # OK
            H2, module_weight2 = create_contraction_subgraph(
                H, module_weight, set())
            if H2.number_of_modules() <= H.number_of_modules():
                part2 = list(0 for _ in range(H2.number_of_modules()))
                H2.projection_up(part, part2)
                legalcheck = self.run_FMPartition(H2, module_weight2, part2,
                                                  limitsize)
                if legalcheck == LegalCheck.allsatisfied:
                    H2.projection_down(part2, part)

        self.totalcost = optimize_fn()
        assert self.totalcost >= 0
        return legalcheck


class MLBiPartMgr(MLPartMgr):
    def __init__(self, BalTol):
        MLPartMgr.__init__(self, FMBiGainCalc, FMBiGainMgr, FMBiConstrMgr,
                           FMPartMgr, BalTol)


class MLKWayPartMgr(MLPartMgr):
    def __init__(self, BalTol, K):
        MLPartMgr.__init__(self, FMKWayGainCalc, FMKWayGainMgr,
                           FMKWayConstrMgr, FMPartMgr, BalTol, K)
