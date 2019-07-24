from .dllist import dllink


class FMBiGainCalc:

    totalcost = None

    # public:

    def __init__(self, H, K=2):
        """Initialization

        Arguments:
            H {Netlist}:  description

        Keyword Arguments:
            K {uint8_t}:  number of partitions (default: {2})
        """
        self.H = H
        self.vertex_list = list(dllink(i)
                                for i in range(self.H.number_of_modules()))

    def init(self, part):
        """(re)initialization after creation

        Arguments:
            part {list}:  description
        """
        self.totalcost = 0
        for vlink in self.vertex_list:
            vlink.key = 0
        for net in self.H.nets:
            # for net in self.H.net_list:
            self.__init_gain(net, part)
        return self.totalcost

    def __init_gain(self, net, part):
        """initialize gain

        Arguments:
            net {node_t}:  description
            part {list}:  description
        """
        degree = self.H.G.degree[net]
        if degree < 2:  # unlikely, self-loop, etc.
            return  # does not provide any gain when move
        if degree == 3:
            self.__init_gain_3pin_net(net, part)
        elif degree == 2:
            self.__init_gain_2pin_net(net, part)
        else:
            self.__init_gain_general_net(net, part)

    def __modify_gain(self, i_w, weight):
        """Modify gain

        Arguments:
            v {node_t}:  description
            weight {int}:  description
        """
        self.vertex_list[i_w].key += weight

    def __init_gain_2pin_net(self, net, part):
        """initialize gain for 2-pin net

        Arguments:
            net {node_t}:  description
            part {list}:  description
        """
        netCur = iter(self.H.G[net])
        w = next(netCur)
        v = next(netCur)
        i_w = self.H.module_map[w]
        i_v = self.H.module_map[v]
        weight = self.H.get_net_weight(net)
        if part[i_w] != part[i_v]:
            self.totalcost += weight
            self.__modify_gain(i_w, weight)
            self.__modify_gain(i_v, weight)
        else:
            self.__modify_gain(i_w, -weight)
            self.__modify_gain(i_v, -weight)

    def __init_gain_3pin_net(self, net, part):
        """initialize gain for 3-pin net

        Arguments:
            net {node_t}:  description
            part {list}:  description
        """
        netCur = iter(self.H.G[net])
        w = next(netCur)
        v = next(netCur)
        u = next(netCur)
        i_w = self.H.module_map[w]
        i_v = self.H.module_map[v]
        i_u = self.H.module_map[u]
        weight = self.H.get_net_weight(net)
        if part[i_u] == part[i_v]:
            if part[i_w] == part[i_v]:
                for i_a in [i_u, i_v, i_w]:
                    self.__modify_gain(i_a, -weight)
                return
            self.__modify_gain(i_w, weight)
        elif part[i_w] == part[i_v]:
            self.__modify_gain(i_u, weight)
        else:  # part[i_u] == part[i_w]
            self.__modify_gain(i_v, weight)
        self.totalcost += weight

    def __init_gain_general_net(self, net, part):
        """initialize gain for general net

        Arguments:
            net {node_t}:  description
            part {list}:  description
        """
        num = [0, 0]
        IdVec = []
        for w in self.H.G[net]:
            i_w = self.H.module_map[w]
            num[part[i_w]] += 1
            IdVec.append(i_w)

        weight = self.H.get_net_weight(net)

        if num[0] > 0 and num[1] > 0:
            self.totalcost += weight

        for k in [0, 1]:
            if num[k] == 0:
                for i_w in IdVec:
                    self.__modify_gain(i_w, -weight)
            elif num[k] == 1:
                for i_w in IdVec:
                    if part[i_w] == k:
                        self.__modify_gain(i_w, weight)
                        break

    def update_move_init(self):
        """update move init

           nothing to do in 2-way partitioning
        """
        pass

    def update_move_2pin_net(self, part, move_info):
        """Update move for 2-pin net

        Arguments:
            part {list}:  description
            move_info {MoveInfoV}:  description

        Returns:
            dtype:  description
        """
        net, fromPart, _, v = move_info
        netCur = iter(self.H.G[net])
        u = next(netCur)
        w = u if u != v else next(netCur)
        i_w = self.H.module_map[w]
        weight = self.H.get_net_weight(net)
        delta = 2 if part[i_w] == fromPart else -2
        return i_w, delta * weight

    def update_move_3pin_net(self, part, move_info):
        """Update move for 3-pin net

        Arguments:
            part {list}:  description
            move_info {MoveInfoV}:  description

        Returns:
            dtype:  description
        """
        net, fromPart, _, v = move_info
        IdVec = []
        deltaGain = []
        for w in self.H.G[net]:
            if w == v:
                continue
            i_w = self.H.module_map[w]
            IdVec.append(i_w)

        deltaGain = [0, 0]
        weight = self.H.get_net_weight(net)

        part_w = part[IdVec[0]]

        if part_w != fromPart:
            weight = -weight

        if part_w == part[IdVec[1]]:
            deltaGain[0] += weight
            deltaGain[1] += weight
        else:
            deltaGain[0] += weight
            deltaGain[1] -= weight

        return IdVec, deltaGain

    def update_move_general_net(self, part, move_info):
        """Update move for general net

        Arguments:
            part {list}:  description
            move_info {MoveInfoV}:  description

        Returns:
            dtype:  description
        """
        net, fromPart, toPart, v = move_info
        num = [0, 0]
        IdVec = []
        deltaGain = []
        for w in self.H.G[net]:
            if w == v:
                continue
            i_w = self.H.module_map[w]
            num[part[i_w]] += 1
            IdVec.append(i_w)

        degree = len(IdVec)
        deltaGain = list(0 for _ in range(degree))
        weight = self.H.get_net_weight(net)

        for l in [fromPart, toPart]:
            if num[l] == 0:
                for idx in range(degree):
                    deltaGain[idx] -= weight
                return IdVec, deltaGain
            elif num[l] == 1:
                for idx in range(degree):
                    part_w = part[IdVec[idx]]
                    if part_w == l:
                        deltaGain[idx] += weight
                        break
            weight = -weight

        return IdVec, deltaGain
