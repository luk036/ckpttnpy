class FMKWayGainCalc:

    # public:

    def __init__(self, H, K):
        """initialization
        
        Arguments:
            H {Netlist} -- [description]
            K {size_t} -- number of partitions
        """
        self.H = H
        self.K = K

    def init(self, part, vertex_list):
        """(re)initialization after creation

        Arguments:
            part {list} -- [description]
        """
        for net in self.H.net_list:
            self.init_gain(net, part, vertex_list)

    def init_gain(self, net, part, vertex_list):
        """initialize gain

        Arguments:
            net {Graph's node} -- [description]
            part {list} -- [description]
        """
        if self.H.G.degree[net] == 2:
            self.init_gain_2pin_net(net, part, vertex_list)
        elif self.H.G.degree[net] < 2:  # unlikely, self-loop, etc.
            return  # does not provide any gain when move
        else:
            self.init_gain_general_net(net, part, vertex_list)

    def init_gain_2pin_net(self, net, part, vertex_list):
        """initialize gain for 2-pin net

        Arguments:
            net {Graph's node} -- [description]
            part {list} -- [description]
        """
        assert self.H.G.degree[net] == 2
        netCur = iter(self.H.G[net])
        w = next(netCur)
        v = next(netCur)
        # i_w = self.H.cell_dict[w]
        # i_v = self.H.cell_dict[v]
        part_w = part[w]
        part_v = part[v]
        weight = self.H.G.nodes[net].get('weight', 1)
        if part_v == part_w:
            for k in range(self.K):
                vertex_list[k][w].key -= weight
                vertex_list[k][v].key -= weight
        vertex_list[part_v][w].key += weight
        vertex_list[part_w][v].key += weight

    def init_gain_general_net(self, net, part, vertex_list):
        """initialize gain for general net

        Arguments:
            net {Graph's node} -- [description]
            part {list} -- [description]
        """
        num = list(0 for _ in range(self.K))
        IdVec = []
        for w in self.H.G[net]:
            # i_w = self.H.cell_dict[w]
            num[part[w]] += 1
            IdVec.append(w)

        weight = self.H.G.nodes[net].get('weight', 1)

        for k in range(self.K):
            if num[k] == 0:
                for w in IdVec:
                    vertex_list[k][w].key -= weight
            elif num[k] == 1:
                for w in IdVec:
                    if part[w] == k:
                        for k2 in range(self.K):
                            vertex_list[k2][w].key += weight
                        break

    def update_move_2pin_net(self, part, move_info):
        """Update move for 2-pin net

        Arguments:
            net {Graph's node} -- [description]
            part {list} -- [description]
            fromPart {int} -- [description]
            v {Graph's node} -- [description]
        """
        net, fromPart, toPart, v = move_info
        assert self.H.G.degree[net] == 2
        netCur = iter(self.H.G[net])
        u = next(netCur)
        w = u if u != v else next(netCur)
        # i_w = self.H.cell_dict[w]
        part_w = part[w]
        weight = self.H.G.nodes[net].get('weight', 1)
        deltaGainW = list(0 for _ in range(self.K))
        if part_w == fromPart:
            for k in range(self.K):
                deltaGainW[k] += weight
        elif part_w == toPart:
            for k in range(self.K):
                deltaGainW[k] -= weight
        deltaGainW[fromPart] -= weight
        deltaGainW[toPart] += weight

        return w, deltaGainW
        # self.gainbucket[1-part_w].modify_key(self.vertex_list[w], deltaGainW)

    def update_move_general_net(self, part, move_info):
        """update move for general net

        Arguments:
            net {Graph's node} -- [description]
            part {list} -- [description]
            fromPart {int} -- [description]
            v {Graph's node} -- [description]
        """
        net, fromPart, toPart, v = move_info
        assert self.H.G.degree[net] > 2
        num = list(0 for _ in range(self.K))
        IdVec = []
        deltaGain = []
        for w in self.H.G[net]:
            if w == v:
                continue
            # i_w = self.H.cell_dict[w]
            num[part[w]] += 1
            IdVec.append(w)

        degree = len(IdVec)
        deltaGain = list(list(0 for _ in range(self.K))
                         for _ in range(degree))

        weight = self.H.G.nodes[net].get('weight', 1)
        # weight = m if fromPart == 0 else -m
        for l in [fromPart, toPart]:
            if num[l] == 0:
                for idx in range(degree):
                    deltaGain[idx][l] -= weight
            elif num[l] == 1:
                for idx in range(degree):
                    part_w = part[IdVec[idx]]
                    if part_w == l:
                        for k in range(self.K):
                            deltaGain[idx][k] += weight
                        break
            weight = -weight

        return IdVec, deltaGain
