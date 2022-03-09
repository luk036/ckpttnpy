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
    def __init__(self, GainCalc, GainMgr, ConstrMgr, PartMgr, bal_tol, num_parts=2):
        """[summary]

        Arguments:
            GainCalc (type):  description
            GainMgr (type):  description
            ConstrMgr (type):  description
            bal_tol (type):  description

        Keyword Arguments:
            num_parts (int):  description (default: {2})
        """
        self.GainCalc = GainCalc
        self.GainMgr = GainMgr
        self.ConstrMgr = ConstrMgr
        self.PartMgr = PartMgr
        self.bal_tol = bal_tol
        self.num_parts = num_parts
        self.totalcost = 0
        self._limitsize = 7

    @property
    def limitsize(self):
        return self._limitsize

    @limitsize.setter
    def limitsize(self, limit):
        self._limitsize = limit

    def run_FMPartition(self, hgr, module_weight, part):
        """[summary]

        Arguments:
            hgr (type):  description
            part (type):  description

        Keyword Arguments:
            limitsize (int):  description (default: {7})

        Returns:
            dtype:  description
        """

        def legalcheck_fn():
            gainMgr = self.GainMgr(self.GainCalc, hgr, self.num_parts)
            constrMgr = self.ConstrMgr(hgr, self.bal_tol, module_weight, self.num_parts)
            partMgr = self.PartMgr(hgr, gainMgr, constrMgr)
            legalcheck = partMgr.legalize(part)
            return legalcheck, partMgr.totalcost

        def optimize_fn():
            gainMgr = self.GainMgr(self.GainCalc, hgr, self.num_parts)
            constrMgr = self.ConstrMgr(hgr, self.bal_tol, module_weight, self.num_parts)
            partMgr = self.PartMgr(hgr, gainMgr, constrMgr)
            partMgr.optimize(part)
            return partMgr.totalcost

        legalcheck, totalcost = legalcheck_fn()
        if legalcheck != LegalCheck.allsatisfied:
            self.totalcost = totalcost
            return legalcheck

        if hgr.number_of_modules() >= self._limitsize:  # OK
            H2, module_weight2 = create_contraction_subgraph(hgr, module_weight, set())
            if H2.number_of_modules() <= hgr.number_of_modules():
                part2 = list(0 for _ in range(H2.number_of_modules()))
                H2.projection_up(part, part2)
                legalcheck_recur = self.run_FMPartition(H2, module_weight2, part2)
                if legalcheck_recur == LegalCheck.allsatisfied:
                    H2.projection_down(part2, part)

        self.totalcost = optimize_fn()
        assert self.totalcost >= 0
        return legalcheck


class MLBiPartMgr(MLPartMgr):
    def __init__(self, bal_tol):
        """[summary]

        Args:
            bal_tol ([type]): [description]
        """
        MLPartMgr.__init__(
            self, FMBiGainCalc, FMBiGainMgr, FMBiConstrMgr, FMPartMgr, bal_tol
        )


class MLKWayPartMgr(MLPartMgr):
    def __init__(self, bal_tol, num_parts):
        """[summary]

        Args:
            bal_tol ([type]): [description]
            num_parts ([type]): [description]
        """
        MLPartMgr.__init__(
            self,
            FMKWayGainCalc,
            FMKWayGainMgr,
            FMKWayConstrMgr,
            FMPartMgr,
            bal_tol,
            num_parts,
        )
