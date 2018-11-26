# Check if the move of v can satisfied, makebetter, or notsatisfied


class FMKWayConstrMgr:
    def __init__(self, H, K, ratio):
        """[summary]

        Arguments:
            H {[type]} -- [description]
            ratio {[type]} -- [description]
        """
        self.H = H
        self.K = K
        self.ratio = ratio
        self.diff = list(0 for _ in range(K))
        self.illegal = list(True for _ in range(K))
        self.upperbound = 0
        self.lowerbound = 0
        self.weight = 0

    def init(self, part):
        """[summary]

        Arguments:
            part {[type]} -- [description]
        """
        totalweight = 0
        for v in self.H.module_list:
            weight = self.H.get_module_weight(v)
            self.diff[part[v]] += weight
            totalweight += weight
        totalweightK = totalweight * 2. / self.K
        self.upperbound = round(totalweightK * self.ratio)
        self.lowerbound = round(totalweightK - self.upperbound)
        for k in range(self.K):
            self.illegal[k] = (self.diff[k] < self.lowerbound or
                               self.diff[k] > self.upperbound)

    def select_togo(self):
        minb = min(self.diff)
        toPart = self.diff.index(minb)
        return toPart

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
        diffTo = self.diff[toPart] + self.weight
        diffFrom = self.diff[fromPart] - self.weight
        if diffTo > self.upperbound or diffFrom < self.lowerbound:
            return 0  # not ok, don't move
        if diffFrom > self.upperbound or diffTo < self.lowerbound:
            return 1  # get better, but still illegal
        self.illegal[fromPart] = self.illegal[toPart] = False
        if any(self.illegal):
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
        fromPart, toPart, v = move_info_v 
        self.weight = self.H.get_module_weight(v)
        diffTo = self.diff[toPart] + self.weight
        diffFrom = self.diff[fromPart] - self.weight
        return diffTo <= self.upperbound and diffFrom >= self.lowerbound

    def update_move(self, move_info_v):
        """[summary]

        Arguments:
            fromPart {[type]} -- [description]
            v {[type]} -- [description]
        """
        fromPart, toPart, _ = move_info_v 
        self.diff[toPart] += self.weight
        self.diff[fromPart] -= self.weight
