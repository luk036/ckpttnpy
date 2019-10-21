# type: ignore

from itertools import permutations
from typing import Any, Dict, List, Union

from .dllist import dllink
from .robin import robin

Part = Union[Dict[Any, int], List[int]]


class FMKWayGainCalc:
    totalcost = 0
    deltaGainV = list()

    # public:

    def __init__(self, H, K: int):
        """initialization

        Arguments:
            H {Netlist}:  description
            K {uint8_t}:  number of partitions
        """
        self.H = H
        self.K = K
        self.RR = robin(K)

        self.vertex_list = []

        if isinstance(self.H.modules, range):
            for _ in range(K):
                self.vertex_list += [
                    list(dllink(i) for i in self.H.modules)
                ]
        elif isinstance(self.H.modules, list):
            for _ in range(K):
                self.vertex_list += [
                    {v: dllink(v) for v in self.H.modules}
                ]
        else:
            raise NotImplementedError

    def init(self, part: Part):
        """(re)initialization after creation

        Arguments:
            part {list}:  description
        """
        self.totalcost = 0

        if isinstance(self.H.modules, range):
            for k in range(self.K):
                for vlink in self.vertex_list[k]:
                    vlink.key = 0
        elif isinstance(self.H.modules, list):
            for k in range(self.K):
                for vlink in self.vertex_list[k].values():
                    vlink.key = 0
        else:
            raise NotImplementedError

        for net in self.H.nets:
            self.__init_gain(net, part)
        return self.totalcost

    def __init_gain(self, net, part: Part):
        """initialize gain

        Arguments:
            net {node_t}:  description
            part {list}:  description
        """
        degree = self.H.G.degree[net]
        if degree < 2:  # unlikely, self-loop, etc.
            return  # does not provide any gain when move
        if degree > 3:
            self.__init_gain_general_net(net, part)
        elif degree == 3:
            self.__init_gain_3pin_net(net, part)
        else:  # degree == 2
            self.__init_gain_2pin_net(net, part)

    def __modify_gain(self, v, pv, weight):
        """Modify gain

        Arguments:
            v {node_t}:  description
            weight {int}:  description
        """
        for k in self.RR.exclude(pv):
            self.vertex_list[k][v].key += weight

    def __init_gain_2pin_net(self, net, part: Part):
        """initialize gain for 2-pin net

        Arguments:
            net {node_t}:  description
            part {list}:  description
        """
        netCur = iter(self.H.G[net])
        w = next(netCur)
        v = next(netCur)
        part_w = part[w]
        part_v = part[v]
        weight = self.H.get_net_weight(net)
        if part_v == part_w:
            for a in [w, v]:
                self.__modify_gain(a, part_v, -weight)
        else:
            self.totalcost += weight
            self.vertex_list[part_v][w].key += weight
            self.vertex_list[part_w][v].key += weight

    def __init_gain_3pin_net(self, net, part: Part):
        """initialize gain for 3-pin net

        Arguments:
            net {node_t}:  description
            part {list}:  description
        """
        netCur = iter(self.H.G[net])
        w = next(netCur)
        v = next(netCur)
        u = next(netCur)
        part_w = part[w]
        part_v = part[v]
        part_u = part[u]
        weight = self.H.get_net_weight(net)
        if part_u == part_v:
            if part_w == part_v:
                for a in [u, v, w]:
                    self.__modify_gain(a, part_v, -weight)
                return
            a, b, c = w, u, v
        elif part_w == part_v:
            a, b, c = u, v, w
        elif part_w == part_u:
            a, b, c = v, w, u
        else:
            self.totalcost += 2 * weight
            for a, b in permutations([u, v, w], 2):
                self.vertex_list[part[b]][a].key += weight
            return

        self.vertex_list[part[b]][a].key += weight
        for e in [b, c]:
            self.__modify_gain(e, part[e], -weight)
            self.vertex_list[part[a]][e].key += weight
        self.totalcost += weight

    def __init_gain_general_net(self, net, part: Part):
        """initialize gain for general net

        Arguments:
            net {node_t}:  description
            part {list}:  description
        """
        num = list(0 for _ in range(self.K))
        IdVec = []
        for w in self.H.G[net]:
            num[part[w]] += 1
            IdVec.append(w)

        weight = self.H.get_net_weight(net)

        for k in range(self.K):
            if num[k] > 0:
                self.totalcost += weight
        self.totalcost -= weight

        for k in range(self.K):
            if num[k] == 0:
                for w in IdVec:
                    self.vertex_list[k][w].key -= weight
            elif num[k] == 1:
                for w in IdVec:
                    if part[w] == k:
                        self.__modify_gain(w, part[w], weight)
                        break

    def update_move_init(self):
        """update move init
        """
        self.deltaGainV = list(0 for _ in range(self.K))

    def update_move_2pin_net(self, part, move_info):
        """Update move for 2-pin net

        Arguments:
            part {list}:  description
            move_info {MoveInfoV}:  description

        Returns:
            dtype:  description
        """
        net, fromPart, toPart, v = move_info
        netCur = iter(self.H.G[net])
        u = next(netCur)
        w = u if u != v else next(netCur)
        part_w = part[w]
        weight = self.H.get_net_weight(net)
        deltaGainW = list(0 for _ in range(self.K))

        for l in [fromPart, toPart]:
            if part_w == l:
                for k in range(self.K):
                    deltaGainW[k] += weight
                    self.deltaGainV[k] += weight
            deltaGainW[l] -= weight
            weight = -weight

        return w, deltaGainW

    def update_move_3pin_net(self, part, move_info):
        """Update move for 3-pin net

        Arguments:
            part {list}:  description
            move_info {MoveInfoV}:  description

        Returns:
            dtype:  description
        """
        net, fromPart, toPart, v = move_info

        IdVec = []
        deltaGain = []
        for w in self.H.G[net]:
            if w == v:
                continue
            IdVec.append(w)

        degree = len(IdVec)
        deltaGain = list(list(0 for _ in range(self.K)) for _ in range(degree))

        weight = self.H.get_net_weight(net)

        l, u = fromPart, toPart

        part_w = part[IdVec[0]]
        part_u = part[IdVec[1]]

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

    def update_move_general_net(self, part, move_info):
        """Update move for general net

        Arguments:
            part {list}:  description
            move_info {MoveInfoV}:  description

        Returns:
            dtype:  description
        """
        net, fromPart, toPart, v = move_info
        num = list(0 for _ in range(self.K))
        IdVec = []
        deltaGain = []
        for w in self.H.G[net]:
            if w == v:
                continue
            num[part[w]] += 1
            IdVec.append(w)

        degree = len(IdVec)
        deltaGain = list(list(0 for _ in range(self.K)) for _ in range(degree))

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
