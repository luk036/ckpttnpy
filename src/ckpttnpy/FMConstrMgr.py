# Check if the move of v can satisfied, makebetter, or notsatisfied


class FMConstrMgr:
    weight = None

    def __init__(self, H, BalTol, K=2):
        """[summary]

        Arguments:
            H (type):  description
            BalTol (type):  description
        """
        self.H = H
        self.BalTol = BalTol
        self.K = K
        self.diff = list(0 for _ in range(K))
        self.totalweight = 0
        for v in range(self.H.number_of_modules()):
            weight = self.H.get_module_weight_by_id(v)
            self.totalweight += weight
        totalweightK = self.totalweight * (2. / self.K)
        self.lowerbound = round(totalweightK * self.BalTol)

    def init(self, part):
        """[summary]

        Arguments:
            part (type):  description
        """
        self.diff = list(0 for _ in range(self.K))
        for i_v in range(self.H.number_of_modules()):
            weight = self.H.get_module_weight_by_id(i_v)
            self.diff[part[i_v]] += weight

    def check_legal(self, move_info_v):
        """[summary]

        Arguments:
            fromPart (type):  description
            v (type):  description

        Returns:
            dtype:  description
        """
        fromPart, toPart, v = move_info_v
        self.weight = self.H.get_module_weight_by_id(v)
        diffFrom = self.diff[fromPart] - self.weight
        if diffFrom < self.lowerbound:
            return 0  # not ok, don't move
        diffTo = self.diff[toPart] + self.weight
        if diffTo < self.lowerbound:
            return 1  # get better, but still illegal
        return 2  # all satisfied

    def check_constraints(self, move_info_v):
        """[summary]

        Arguments:
            fromPart (type):  description
            v (type):  description

        Returns:
            dtype:  description
        """
        fromPart, _, v = move_info_v
        self.weight = self.H.get_module_weight_by_id(v)
        diffFrom = self.diff[fromPart] - self.weight
        return diffFrom >= self.lowerbound

    def update_move(self, move_info_v):
        """[summary]

        Arguments:
            fromPart (type):  description
            v (type):  description
        """
        fromPart, toPart, _ = move_info_v
        self.diff[toPart] += self.weight
        self.diff[fromPart] -= self.weight
