# **Special code for two-pin nets**
# Take a snapshot when a move make **negative** gain.
# Snapshot in the form of "interface"???
from .min_cover import create_contraction_subgraph
from .FMPartMgr import FMPartMgr
from .FMBiGainMgr2 import FMBiGainMgr2
from .FMBiGainCalc import FMBiGainCalc
from .FMBiConstrMgr import FMBiConstrMgr
from .FMKWayGainMgr import FMKWayGainMgr
from .FMKWayGainCalc import FMKWayGainCalc
from .FMKWayConstrMgr import FMKWayConstrMgr


class MLPartMgr:
    def __init__(self, BalTol, K=2):
        """[summary]

        Arguments:
            H {[type]} -- [description]
            gainMgr {[type]} -- [description]
            constrMgr {[type]} -- [description]
        """
        self.BalTol = BalTol
        self.K = K
        self.snapshot = None
        self.totalcost = 0

    def run_BiPartition(self, H, part):
        gainMgr = FMBiGainMgr2(FMBiGainCalc, H)
        constrMgr = FMBiConstrMgr(H, self.BalTol)
        partMgr = FMPartMgr(H, gainMgr, constrMgr)
        partMgr.init(part)
        legalcheck = partMgr.legalize(part)
        if legalcheck == 2 and H.number_of_modules() >= 3: # OK
            H2 = create_contraction_subgraph(H)
            part2 = list(0 for _ in range(H2.number_of_modules()))
            H2.project_up(part, part2)
            legalcheck = self.run_BiPartition(H2, part2)
            H2.project_down(part2, part)
            partMgr.init(part)
            if legalcheck != 2:
                legalcheck = partMgr.legalize(part)
                assert partMgr.totalcost >= 0
        partMgr.optimize(part)
        assert partMgr.totalcost >= 0
        self.totalcost = partMgr.totalcost
        return legalcheck

    def run_KWayPartition(self, H, part):
        gainMgr = FMKWayGainMgr(FMKWayGainCalc, H, self.K)
        constrMgr = FMKWayConstrMgr(H, self.BalTol, self.K)
        partMgr = FMPartMgr(H, gainMgr, constrMgr)
        partMgr.init(part)
        legalcheck = partMgr.legalize(part)
        if legalcheck == 2 and H.number_of_modules() >= 3: # OK
            H2 = create_contraction_subgraph(H)
            part2 = list(0 for _ in range(H2.number_of_modules()))
            H2.project_up(part, part2)
            legalcheck = self.run_KWayPartition(H2, part2)
            H2.project_down(part2, part)
            partMgr.init(part)
            if legalcheck != 2:
                legalcheck = partMgr.legalize(part)
                assert partMgr.totalcost >= 0
        partMgr.optimize(part)
        assert partMgr.totalcost >= 0
        self.totalcost = partMgr.totalcost
        return legalcheck
