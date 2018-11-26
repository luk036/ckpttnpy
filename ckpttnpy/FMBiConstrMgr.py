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
        for v in self.H.module_list:
            weight = self.H.get_module_weight(v)
            self.diff[part[v]] += weight
            totalweight += weight
        self.upperbound = round(totalweight * self.ratio)

    def select(self):
        """[summary]

        Returns:
            [type] -- [description]
        """
        return 0 if self.diff[0] < self.diff[1] else 1

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
        if diffTo > self.upperbound:
            return 0
        diffFrom = self.diff[fromPart] - self.weight
        if diffFrom > self.upperbound:
            return 1
        return 2

    def check_constraints(self, move_info_v):
        """[summary]

        Arguments:
            fromPart {[type]} -- [description]
            v {[type]} -- [description]

        Returns:
            [type] -- [description]
        """
        _, toPart, v = move_info_v
        self.weight = self.H.get_module_weight(v)
        return self.diff[toPart] + self.weight <= self.upperbound

    def update_move(self, move_info_v):
        """[summary]

        Arguments:
            fromPart {[type]} -- [description]
            v {[type]} -- [description]
        """
        fromPart, toPart, _ = move_info_v
        self.diff[toPart] += self.weight
        self.diff[fromPart] -= self.weight
