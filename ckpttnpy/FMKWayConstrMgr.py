# Check if the move of v can satisfied, makebetter, or notsatisfied


class FMKWayConstrMgr:
    def __init__(self, K, H, ratio):
        """[summary]

        Arguments:
            H {[type]} -- [description]
            ratio {[type]} -- [description]
        """
        self.K = K
        self.H = H
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
        for v in self.H.cell_list:
            weight = self.H.G.nodes[v].get('weight', 1)
            # weight = 10
            self.diff[part[v]] += weight
            totalweight += weight
        totalweightK = totalweight * 2. / self.K
        self.upperbound = round(totalweightK * self.ratio)
        self.lowerbound = round(totalweightK - self.upperbound)
        for k in range(self.K):
            self.illegal[k] = (self.diff[k] < self.lowerbound or
                               self.diff[k] > self.upperbound)

    def check_legal(self, fromPart, toPart, v):
        """[summary]

        Arguments:
            fromPart {[type]} -- [description]
            v {[type]} -- [description]

        Returns:
            [type] -- [description]
        """
        self.weight = self.H.G.nodes[v].get('weight', 1)
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

    def check_constraints(self, fromPart, toPart, v):
        """[summary]

        Arguments:
            fromPart {[type]} -- [description]
            v {[type]} -- [description]

        Returns:
            [type] -- [description]
        """
        self.weight = self.H.G.nodes[v].get('weight', 1)
        # toPart = 1 - fromPart
        diffTo = self.diff[toPart] + self.weight
        diffFrom = self.diff[fromPart] + self.weight
        return diffTo <= self.upperbound and diffFrom >= self.lowerbound

    def update_move(self, fromPart, toPart, v):
        """[summary]

        Arguments:
            fromPart {[type]} -- [description]
            v {[type]} -- [description]
        """
        self.weight = self.H.G.nodes[v].get('weight', 1)
        # toPart = 1 - fromPart
        self.diff[toPart] += self.weight
        self.diff[fromPart] -= self.weight
