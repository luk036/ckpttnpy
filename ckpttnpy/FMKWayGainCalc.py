from .dllist import dllink
from .robin import robin
from itertools import permutations

class FMKWayGainCalc:

    totalcost = 0
    deltaGainV = list()

    # public:

    def __init__(self, H, K):
        """initialization

        Arguments:
            H {Netlist} -- [description]
            K {uint8_t} -- number of partitions
        """
        self.H = H
        self.K = K
        self.RR = robin(K)

        self.vertex_list = []
        for _ in range(K):
            self.vertex_list += [list(dllink(i)
                                      for i in range(self.H.number_of_modules()))]

    def init(self, part_info):
        """(re)initialization after creation

        Arguments:
            part {list} -- [description]
        """
        self.totalcost = 0
        for k in range(self.K):
            for vlink in self.vertex_list[k]:
                vlink.key = 0

        for net in self.H.nets:
            self.init_gain(net, part_info)
        return self.totalcost

    def init_gain(self, net, part_info):
        """initialize gain

        Arguments:
            net {node_t} -- [description]
            part {list} -- [description]
        """
        degree = self.H.G.degree[net]
        if degree < 2:  # unlikely, self-loop, etc.
            return  # does not provide any gain when move
        part, _ = part_info
        if degree > 3:
            self.init_gain_general_net(net, part)
        elif degree == 3:
            self.init_gain_3pin_net(net, part)
        else:  # degree == 2
            self.init_gain_2pin_net(net, part)

    def modify_gain(self, i_v, pv, weight):
        """Modify gain

        Arguments:
            v {node_t} -- [description]
            weight {int} -- [description]
        """
        for k in self.RR.exclude(pv):
            self.vertex_list[k][i_v].key += weight

    def init_gain_2pin_net(self, net, part):
        """initialize gain for 2-pin net

        Arguments:
            net {node_t} -- [description]
            part {list} -- [description]
        """
        netCur = iter(self.H.G[net])
        w = next(netCur)
        v = next(netCur)
        i_w = self.H.module_map[w]
        i_v = self.H.module_map[v]
        part_w = part[i_w]
        part_v = part[i_v]
        weight = self.H.get_net_weight(net)
        if part_v == part_w:
            for i_a in [i_w, i_v]:
                self.modify_gain(i_a, part_v, -weight)
        else:
            self.totalcost += weight
            self.vertex_list[part_v][i_w].key += weight
            self.vertex_list[part_w][i_v].key += weight

    def init_gain_3pin_net(self, net, part):
        """initialize gain for 3-pin net

        Arguments:
            net {node_t} -- [description]
            part {list} -- [description]
        """
        netCur = iter(self.H.G[net])
        w = next(netCur)
        v = next(netCur)
        u = next(netCur)
        i_w = self.H.module_map[w]
        i_v = self.H.module_map[v]
        i_u = self.H.module_map[u]
        part_w = part[i_w]
        part_v = part[i_v]
        part_u = part[i_u]
        weight = self.H.get_net_weight(net)
        if part_u == part_v:
            if part_w == part_v:
                for i_a in [i_u, i_v, i_w]:
                    self.modify_gain(i_a, part_v, -weight)
                return
            i_a, i_b, i_c = i_w, i_u, i_v
        elif part_w == part_v:
            i_a, i_b, i_c = i_u, i_v, i_w
        elif part_w == part_u:
            i_a, i_b, i_c = i_v, i_w, i_u
        else:
            self.totalcost += 2 * weight
            for i_a, i_b in permutations([i_u, i_v, i_w], 2):
                self.vertex_list[part[i_b]][i_a].key += weight
            return

        self.vertex_list[part[i_b]][i_a].key += weight
        for i_e in [i_b, i_c]:
            self.modify_gain(i_e, part[i_e], -weight)
            self.vertex_list[part[i_a]][i_e].key += weight
        self.totalcost += weight

    def init_gain_general_net(self, net, part):
        """initialize gain for general net

        Arguments:
            net {node_t} -- [description]
            part {list} -- [description]
        """
        num = list(0 for _ in range(self.K))
        IdVec = []
        for w in self.H.G[net]:
            i_w = self.H.module_map[w]
            num[part[i_w]] += 1
            IdVec.append(i_w)

        weight = self.H.get_net_weight(net)

        for k in range(self.K):
            if num[k] > 0:
                self.totalcost += weight
        self.totalcost -= weight

        for k in range(self.K):
            if num[k] == 0:
                for i_w in IdVec:
                    self.vertex_list[k][i_w].key -= weight
            elif num[k] == 1:
                for i_w in IdVec:
                    if part[i_w] == k:
                        self.modify_gain(i_w, part[i_w], weight)
                        break

    def update_move_init(self):
        """update move init
        """
        self.deltaGainV = list(0 for _ in range(self.K))

    def update_move_2pin_net(self, part_info, move_info):
        """Update move for 2-pin net

        Arguments:
            part {list} -- [description]
            move_info {MoveInfoV} -- [description]

        Returns:
            [type] -- [description]
        """
        net, fromPart, toPart, v = move_info
        part, _ = part_info
        netCur = iter(self.H.G[net])
        u = next(netCur)
        w = u if u != v else next(netCur)
        i_w = self.H.module_map[w]
        part_w = part[i_w]
        weight = self.H.get_net_weight(net)
        deltaGainW = list(0 for _ in range(self.K))
        # deltaGainV = list(0 for _ in range(self.K))

        for l in [fromPart, toPart]:
            if part_w == l:
                for k in range(self.K):
                    deltaGainW[k] += weight
                    self.deltaGainV[k] += weight
            deltaGainW[l] -= weight
            weight = -weight

        return i_w, deltaGainW

    def update_move_3pin_net(self, part_info, move_info):
        """Update move for 3-pin net

        Arguments:
            part {list} -- [description]
            move_info {MoveInfoV} -- [description]

        Returns:
            [type] -- [description]
        """
        net, fromPart, toPart, v = move_info
        part, _ = part_info

        IdVec = []
        deltaGain = []
        for w in self.H.G[net]:
            if w == v:
                continue
            i_w = self.H.module_map[w]
            IdVec.append(i_w)

        degree = len(IdVec)
        deltaGain = list(list(0 for _ in range(self.K))
                         for _ in range(degree))

        weight = self.H.get_net_weight(net)

        l, u = fromPart, toPart

        part_w = part[IdVec[0]]
        part_u = part[IdVec[1]]

        # action = [extern_nets.add, extern_nets.remove]
        if part_w == part_u:
            for _ in [0, 1]:
                if part_w != l:
                    deltaGain[0][l] -= weight
                    deltaGain[1][l] -= weight
                    if part_w == u:
                        for k in range(self.K):
                            self.deltaGainV[k] -= weight
                weight = -weight
                l, u = u, l
            return IdVec, deltaGain

        for _ in [0, 1]:
            if part_w == l:
                for k in range(self.K):
                    deltaGain[0][k] += weight
            elif part_u == l:
                for k in range(self.K):
                    deltaGain[1][k] += weight
            else:
                deltaGain[0][l] -= weight
                deltaGain[1][l] -= weight
                if part_w == u or part_u == u:
                    for k in range(self.K):
                        self.deltaGainV[k] -= weight
            weight = -weight
            l, u = u, l

        return IdVec, deltaGain
        # return self.update_move_general_net(part_info, move_info)

    def update_move_general_net(self, part_info, move_info):
        """Update move for general net

        Arguments:
            part {list} -- [description]
            move_info {MoveInfoV} -- [description]

        Returns:
            [type] -- [description]
        """
        net, fromPart, toPart, v = move_info
        part, _ = part_info
        num = list(0 for _ in range(self.K))
        IdVec = []
        deltaGain = []
        for w in self.H.G[net]:
            if w == v:
                continue
            i_w = self.H.module_map[w]
            num[part[i_w]] += 1
            IdVec.append(i_w)

        degree = len(IdVec)
        deltaGain = list(list(0 for _ in range(self.K))
                         for _ in range(degree))

        weight = self.H.get_net_weight(net)

        l, u = fromPart, toPart
        for _ in [0, 1]:
            if num[l] == 0:
                for idx in range(degree):
                    deltaGain[idx][l] -= weight
                if num[u] > 0:
                    for k in range(self.K):
                        self.deltaGainV[k] -= weight
            elif num[l] == 1:
                for idx in range(degree):
                    part_w = part[IdVec[idx]]
                    if part_w == l:
                        for k in range(self.K):
                            deltaGain[idx][k] += weight
                        break
            weight = -weight
            l, u = u, l

        return IdVec, deltaGain
