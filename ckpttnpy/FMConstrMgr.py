# Check if the move of v can satisfied, makebetter, or notsatisfied


class FMConstrMgr:
    def __init__(self, H, ratio, K=2):
        """[summary]

        Arguments:
            H {[type]} -- [description]
            ratio {[type]} -- [description]
        """
        self.H = H
        self.ratio = ratio
        self.K = K
        self.diff = list(0 for _ in range(K))
        # self.illegal = list(True for _ in range(K))
        self.lowerbound = 0
        self.weight = 0

    def init(self, part):
        """[summary]

        Arguments:
            part {[type]} -- [description]
        """
        totalweight = 0
        for v in range(self.H.number_of_modules()):
            weight = self.H.get_module_weight(v)
            self.diff[part[v]] += weight
            totalweight += weight
        totalweightK = totalweight * (2. / self.K)
        self.lowerbound = round(totalweightK * self.ratio)

        # for k in range(self.K):
        #     self.illegal[k] = (self.diff[k] < self.lowerbound)

    # def select_togo(self):
    #     minb = min(self.diff)
    #     return self.diff.index(minb)

    def check_legal(self, move_info_v):
        """[summary]

        Arguments:
            fromPart {[type]} -- [description]
            v {[type]} -- [description]

        Returns:
            [type] -- [description]
        """
        fromPart, toPart, v = move_info_v
        self.weight = self.H.get_module_weight(v)
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
            fromPart {[type]} -- [description]
            v {[type]} -- [description]

        Returns:
            [type] -- [description]
        """
        fromPart, _, v = move_info_v
        self.weight = self.H.get_module_weight(v)
        diffFrom = self.diff[fromPart] - self.weight
        return diffFrom >= self.lowerbound

    def update_move(self, move_info_v):
        """[summary]

        Arguments:
            fromPart {[type]} -- [description]
            v {[type]} -- [description]
        """
        fromPart, toPart, _ = move_info_v
        self.diff[toPart] += self.weight
        self.diff[fromPart] -= self.weight
