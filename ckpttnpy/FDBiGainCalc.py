from .dllist import dllink


class FDBiGainCalc:

    totalcost = 0

    # public:

    def __init__(self, H, K=2):
        """Initialization

        Arguments:
            H {Netlist} -- [description]

        Keyword Arguments:
            K {uint8_t} -- number of partitions (default: {2})
        """
        self.H = H
        self.vertex_list = list(dllink(i)
                                for i in range(self.H.number_of_modules()))

    def init(self, part_info):
        """(re)initialization after creation

        Arguments:
            part_info {[type]} -- [description]
        """
        for vlink in self.vertex_list:
            vlink.key = 0

        self.totalcost = 0
        for net in self.H.nets:
            # for net in self.H.net_list:
            self.init_gain(net, part_info)
        return self.totalcost

    def init_gain(self, net, part_info):
        """initialize gain

        Arguments:
            net {node_t} -- [description]
            part_info {[type]} -- [description]
        """
        degree = self.H.G.degree[net]
        if degree < 2:  # unlikely, self-loop, etc.
            return  # does not provide any gain when move
        part, extern_nets = part_info
        weight = self.H.get_net_weight(net)
        if net in extern_nets:
            self.totalcost += weight
            if degree == 3:
                self.init_gain_3pin_net(net, part, weight)
            elif degree == 2:
                for w in self.H.G[net]:
                    i_w = self.H.module_map[w]
                    self.modify_gain(i_w, weight)
            else:
                self.init_gain_general_net(net, part, weight)
        else:  # 90%
            for w in self.H.G[net]:
                i_w = self.H.module_map[w]
                self.modify_gain(i_w, -weight)

    def init_gain_3pin_net(self, net, part, weight):
        """initialize gain for 3-pin net

        Arguments:
            net {node_t} -- [description]
            part {list} -- [description]
            weight {int} -- [description]
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
            self.modify_gain(i_w, weight)
        elif part[i_w] == part[i_v]:
            self.modify_gain(i_u, weight)
        else:  # part[i_u] == part[i_w]
            self.modify_gain(i_v, weight)

    def init_gain_general_net(self, net, part, weight):
        """initialize gain for general net

        Arguments:
            net {node_t} -- [description]
            part {list} -- [description]
            weight {int} -- [description]
        """
        num = [0, 0]
        IdVec = []
        for w in self.H.G[net]:
            i_w = self.H.module_map[w]
            num[part[i_w]] += 1
            IdVec.append(i_w)

        for k in [0, 1]:
            if num[k] == 1:
                for i_w in IdVec:
                    if part[i_w] == k:
                        self.modify_gain(i_w, weight)
                        break

    def modify_gain(self, i_w, weight):
        """Modify gain

        Arguments:
            v {node_t} -- [description]
            weight {int} -- [description]
        """
        self.vertex_list[i_w].key += weight

    def update_move_init(self):
        """update move init

           nothing to do in 2-way partitioning
        """
        pass

    def update_move_2pin_net(self, part_info, move_info):
        """Update move for 2-pin net

        Arguments:
            part_info {[type]} -- [description]
            move_info {MoveInfoV} -- [description]

        Returns:
            [type] -- [description]
        """
        part, extern_nets = part_info
        net, fromPart, _, v = move_info
        netCur = iter(self.H.G[net])
        u = next(netCur)
        w = u if u != v else next(netCur)
        weight = self.H.get_net_weight(net)
        i_w = self.H.module_map[w]
        if part[i_w] == fromPart:
            extern_nets.add(net)
            weight *= 2
        else:
            extern_nets.remove(net)
            weight *= -2
        return i_w, weight

    def update_move_3pin_net(self, part_info, move_info):
        """Update move for 3-pin net

        Arguments:
            part {list} -- [description]
            move_info {MoveInfoV} -- [description]

        Returns:
            [type] -- [description]
        """
        net, fromPart, _, v = move_info
        part, extern_nets = part_info
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
        if part_w == part[IdVec[1]]:
            if part_w == fromPart:
                extern_nets.add(net)
                deltaGain[0] += weight
                deltaGain[1] += weight
            else:  # part_w == toPart
                extern_nets.remove(net)
                deltaGain[0] -= weight
                deltaGain[1] -= weight
        else:
            if part_w == fromPart:
                deltaGain[0] += weight
                deltaGain[1] -= weight
            else:  # part_w == toPart
                deltaGain[0] -= weight
                deltaGain[1] += weight
        return IdVec, deltaGain

    def update_move_general_net(self, part_info, move_info):
        """Update move for general net

        Arguments:
            part_info {[type]} -- [description]
            move_info {MoveInfoV} -- [description]

        Returns:
            [type] -- [description]
        """
        net, fromPart, toPart, v = move_info
        part, extern_nets = part_info
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

        action = [extern_nets.remove, extern_nets.add]
        l, u = fromPart, toPart
        for i in [0, 1]:
            if num[l] == 0:
                action[i](net)
                for idx in range(degree):
                    deltaGain[idx] -= weight
            elif num[l] == 1:
                for idx in range(degree):
                    part_w = part[IdVec[idx]]
                    if part_w == l:
                        deltaGain[idx] += weight
                        break
            weight = -weight
            l, u = u, l

        return IdVec, deltaGain
