# Check if the move of v can satisfied, makebetter, or notsatisfied


class FMBiConstrMgr:
    def __init__(self, H, ratio):
        self.H = H
        self.ratio = ratio
        self.diff = [0, 0]
        self.upperbound = 0
        self.lowerbound = 0

    def init(self, part):
        totalweight = 0
        for v in self.H.cell_list:
            weight = self.H.G.nodes[v].get('weight', 1)
            # weight = 10
            self.diff[part[v]] += weight
            totalweight += weight
        self.lowerbound = round(totalweight * self.ratio)
        self.upperbound = totalweight - self.lowerbound

    def check_legal(self, fromPart, v):
        weight = self.H.G.nodes[v].get('weight', 1)
        # weight = 10
        toPart = 1 - fromPart
        diffToBefore = self.diff[toPart]
        diffToAfter = diffToBefore + weight
        diffFromBefore = self.diff[fromPart]
        diffFromAfter = diffFromBefore - weight
        if diffToAfter <= self.upperbound and diffFromAfter >= self.lowerbound:
            return 2  # constraints satisfied
        if abs(diffFromAfter - diffToAfter) < abs(diffFromBefore - diffToBefore):
            return 1  # get better
        return 0  # not ok

    def check_constraints(self, fromPart, v):
        weight = self.H.G.nodes[v].get('weight', 1)
        toPart = 1 - fromPart
        return (self.diff[toPart] + weight <= self.upperbound
                and self.diff[fromPart] - weight >= self.lowerbound)

    def update_move(self, fromPart, v):
        weight = self.H.G.nodes[v].get('weight', 1)
        toPart = 1 - fromPart
        self.diff[toPart] += weight
        self.diff[fromPart] -= weight
