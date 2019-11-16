# type: ignore

# **Special code for two-pin nets**
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

    def run_FMPartition(self, H, part, limitsize=7):
        """[summary]

        Arguments:
            H (type):  description
            part (type):  description

        Keyword Arguments:
            limitsize (int):  description (default: {7})

        Returns:
            dtype:  description
        """
        gainMgr = self.GainMgr(self.GainCalc, H, self.K)
        constrMgr = self.ConstrMgr(H, self.BalTol, self.K)
        partMgr = self.PartMgr(H, gainMgr, constrMgr)
        legalcheck = partMgr.legalize(part)
        if legalcheck != 2:
            return legalcheck
        if H.number_of_modules() >= limitsize:  # OK
            H2 = create_contraction_subgraph(H, set())
            if 5 * H2.number_of_modules() <= 3 * H.number_of_modules():
                part2 = list(0 for _ in range(H2.number_of_modules()))
                H2.projection_up(part, part2)
                legalcheck = self.run_FMPartition(H2, part2, limitsize)
                if legalcheck == 2:
                    H2.projection_down(part2, part)
        partMgr.optimize(part)
        assert partMgr.totalcost >= 0
        self.totalcost = partMgr.totalcost
        return legalcheck

    # def run_Partition(self, H, part, limitsize=7):
    #     """[summary]

    #     Arguments:
    #         H (type):  description
    #         part (type):  description

    #     Keyword Arguments:
    #         limitsize (int):  description (default: {7})

    #     Returns:
    #         dtype:  description
    #     """
    #     gainMgr = self.GainMgr(self.GainCalc, H, self.K)
    #     constrMgr = self.ConstrMgr(H, self.BalTol, self.K)
    #     partMgr = self.PartMgr(H, gainMgr, constrMgr)
    #     legalcheck = partMgr.legalize(part)
    #     assert partMgr.totalcost > 0
    #     if legalcheck != 2:
    #         self.totalcost = partMgr.totalcost
    #         return legalcheck
    #     self.run_Partition_recur(H, part, limitsize)
    #     return legalcheck

    # def run_Partition_recur(self, H, part, limitsize=7):
    #     if H.number_of_modules() >= limitsize:  # OK
    #         H2 = create_contraction_subgraph(H)
    #         if 5 * H2.number_of_modules() <= 3 * H.number_of_modules():
    #             part2 = list(0 for _ in range(H2.number_of_modules()))
    #             extern_nets2 = set()
    #             part2_info = part2, extern_nets2
    #             H2.projection_up(part, part2)
    #             self.run_Partition_recur(H2, part2, limitsize)
    #             H2.projection_down(part2, part)

    #     gainMgr = self.GainMgr(self.GainCalc, H, self.K)
    #     constrMgr = self.ConstrMgr(H, self.BalTol, self.K)
    #     partMgr = self.PartMgr(H, gainMgr, constrMgr)
    #     partMgr.optimize(part)
    #     self.totalcost = partMgr.totalcost
    #     assert partMgr.totalcost > 0
