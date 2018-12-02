from .dllist import dllink


class FMKWayGainCalc:

    # public:

    def __init__(self, H, K):
        """initialization

        Arguments:
            H {Netlist} -- [description]
            K {uint8_t} -- number of partitions
        """
        self.H = H
        self.K = K

        num_modules = H.number_of_modules()
        self.vertex_list = []
        for _ in range(K):
            self.vertex_list += [list(dllink(i) for i in range(num_modules))]

        self.deltaGainV = list()

    def init(self, part):
        """(re)initialization after creation

        Arguments:
            part {list} -- [description]
        """
        for net in self.H.net_list:
            self.init_gain(net, part)

    def init_gain(self, net, part):
        """initialize gain

        Arguments:
            net {node_t} -- [description]
            part {list} -- [description]
        """
        if self.H.G.degree[net] == 2:
            self.init_gain_2pin_net(net, part)
        elif self.H.G.degree[net] < 2:  # unlikely, self-loop, etc.
            return  # does not provide any gain when move
        else:
            self.init_gain_general_net(net, part)

    def set_key(self, v, key):
        """[summary]

        Arguments:
            v {[type]} -- [description]
            key {[type]} -- [description]
        """
        for k in range(self.K):
            self.vertex_list[k][v].key = key

    def modify_gain(self, v, weight):
        """Modify gain

        Arguments:
            v {node_t} -- [description]
            weight {int} -- [description]
        """
        for k in range(self.K):
            self.vertex_list[k][v].key += weight

    def init_gain_2pin_net(self, net, part):
        """initialize gain for 2-pin net

        Arguments:
            net {node_t} -- [description]
            part {list} -- [description]
        """
        assert self.H.G.degree[net] == 2
        netCur = iter(self.H.G[net])
        w = next(netCur)
        v = next(netCur)
        # i_w = self.H.module_dict[w]
        # i_v = self.H.module_dict[v]
        part_w = part[w]
        part_v = part[v]
        weight = self.H.get_net_weight(net)
        if part_v == part_w:
            self.modify_gain(w, -weight)
            self.modify_gain(v, -weight)
        self.vertex_list[part_v][w].key += weight
        self.vertex_list[part_w][v].key += weight

    def init_gain_general_net(self, net, part):
        """initialize gain for general net

        Arguments:
            net {node_t} -- [description]
            part {list} -- [description]
        """
        num = list(0 for _ in range(self.K))
        IdVec = []
        for w in self.H.G[net]:
            # i_w = self.H.module_dict[w]
            num[part[w]] += 1
            IdVec.append(w)

        weight = self.H.get_net_weight(net)

        for k in range(self.K):
            if num[k] == 0:
                for w in IdVec:
                    self.vertex_list[k][w].key -= weight
            elif num[k] == 1:
                for w in IdVec:
                    if part[w] == k:
                        self.modify_gain(w, weight)
                        break

    def update_move_init(self):
        """update move init
        """
        self.deltaGainV = list(0 for _ in range(self.K))

    def update_move_2pin_net(self, part, move_info):
        """Update move for 2-pin net

        Arguments:
            part {list} -- [description]
            move_info {MoveInfoV} -- [description]

        Returns:
            [type] -- [description]
        """
        net, fromPart, toPart, v = move_info
        assert self.H.G.degree[net] == 2
        netCur = iter(self.H.G[net])
        u = next(netCur)
        w = u if u != v else next(netCur)
        part_w = part[w]
        weight = self.H.get_net_weight(net)
        deltaGainW = list(0 for _ in range(self.K))
        # deltaGainV = list(0 for _ in range(self.K))
        if part_w == fromPart:
            for k in range(self.K):
                deltaGainW[k] += weight
                self.deltaGainV[k] += weight

        elif part_w == toPart:
            for k in range(self.K):
                deltaGainW[k] += weight
                self.deltaGainV[k] += weight

        deltaGainW[fromPart] -= weight
        deltaGainW[toPart] += weight
        return w, deltaGainW

    def update_move_general_net(self, part, move_info):
        """Update move for general net

        Arguments:
            part {list} -- [description]
            move_info {MoveInfoV} -- [description]

        Returns:
            [type] -- [description]
        """
        net, fromPart, toPart, v = move_info
        assert self.H.G.degree[net] > 2
        num = list(0 for _ in range(self.K))
        IdVec = []
        deltaGain = []
        for w in self.H.G[net]:
            if w == v:
                continue
            num[part[w]] += 1
            IdVec.append(w)

        degree = len(IdVec)
        deltaGain = list(list(0 for _ in range(self.K))
                         for _ in range(degree))
        # deltaGainV = list(0 for _ in range(self.K))

        weight = self.H.get_net_weight(net)

        if num[fromPart] == 0:
            if num[toPart] > 0:
                for idx in range(degree):
                    deltaGain[idx][fromPart] -= weight
                for k in range(self.K):
                    self.deltaGainV[k] -= weight
        else:
            if num[toPart] == 0:
                for idx in range(degree):
                    deltaGain[idx][toPart] += weight
                for k in range(self.K):
                    self.deltaGainV[k] += weight

        for l in [fromPart, toPart]:
            if num[l] == 1:
                for idx in range(degree):
                    part_w = part[IdVec[idx]]
                    if part_w == l:
                        for k in range(self.K):
                            deltaGain[idx][k] += weight
                        break
            weight = -weight

        return IdVec, deltaGain
