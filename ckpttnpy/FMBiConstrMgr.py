# Check if the move of v can satisfied, makebetter, or notsatisfied


class FMBiConstrMgr:
    def __init__(self, H, ratio):
        """[summary]

        Arguments:
            H {[type]} -- [description]
            ratio {[type]} -- [description]
        """
        self.H = H
        self.ratio = ratio
        self.diff = [0, 0]
        self.upperbound = 0
        self.weight = 0  # cache value

    def init(self, part):
        """[summary]

        Arguments:
            part {[type]} -- [description]
        """
        totalweight = 0
        for v in self.H.cell_list:
            weight = self.H.G.nodes[v].get('weight', 1)
            self.diff[part[v]] += weight
            totalweight += weight
        self.upperbound = round(totalweight * self.ratio)

    def pick_move(self):
        return 0 if self.diff[0] < self.diff[1] else 1

    def check_legal(self, fromPart, v):
        """[summary]

        Arguments:
            fromPart {[type]} -- [description]
            v {[type]} -- [description]

        Returns:
            [type] -- [description]
        """
        self.weight = self.H.G.nodes[v].get('weight', 1)
        # weight = 10
        toPart = 1 - fromPart
        diffTo = self.diff[toPart] + self.weight
        if diffTo > self.upperbound:
            return 0
        diffFrom = self.diff[fromPart] - self.weight
        if diffFrom > self.upperbound:
            return 1
        return 2

    def check_constraints(self, fromPart, v):
        """[summary]

        Arguments:
            fromPart {[type]} -- [description]
            v {[type]} -- [description]

        Returns:
            [type] -- [description]
        """
        self.weight = self.H.G.nodes[v].get('weight', 1)
        toPart = 1 - fromPart
        return self.diff[toPart] + self.weight <= self.upperbound

    def update_move(self, fromPart, v):
        """[summary]

        Arguments:
            fromPart {[type]} -- [description]
            v {[type]} -- [description]
        """
        # weight = self.H.G.nodes[v].get('weight', 1)
        toPart = 1 - fromPart
        self.diff[toPart] += self.weight
        self.diff[fromPart] -= self.weight
