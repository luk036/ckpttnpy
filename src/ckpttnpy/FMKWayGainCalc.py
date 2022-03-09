# type: ignore

from itertools import permutations
from typing import Any, Dict, List, Union

from .dllist import Dllink
from .robin import robin

Part = Union[Dict[Any, int], List[int]]


class FMKWayGainCalc:

    __slots__ = (
        "totalcost",
        "hgr",
        "vertex_list",
        "K",
        "RR",
        "deltaGainV",
        "IdVec",
        "deltaGainW",
    )

    # public:

    def __init__(self, hgr, K: int):
        """initialization

        Arguments:
            hgr (Netlist):  description
            K (uint8_t):  number of partitions
        """
        self.deltaGainV = list()

        self.hgr = hgr
        self.K = K
        self.RR = robin(K)

        self.vertex_list = []

        if isinstance(self.hgr.modules, range):
            self.vertex_list = [[Dllink([0, i]) for i in self.hgr] for _ in range(K)]
        elif isinstance(self.hgr.modules, list):
            self.vertex_list = [{v: Dllink([0, v]) for v in self.hgr} for _ in range(K)]
        else:
            raise NotImplementedError

    def init(self, part: Part):
        """(re)initialization after creation

        Arguments:
            part (list):  description
        """
        self.totalcost = 0

        if isinstance(self.hgr.modules, range):
            for vlist in self.vertex_list:
                for vlink in vlist:
                    vlink.data[0] = 0
        elif isinstance(self.hgr.modules, list):
            for vlist in self.vertex_list:
                for vlink in vlist.values():
                    vlink.data[0] = 0
        else:
            raise NotImplementedError

        for net in self.hgr.nets:
            self._init_gain(net, part)
        return self.totalcost

    def _init_gain(self, net, part: Part):
        """initialize gain

        Arguments:
            net (node_t):  description
            part (list):  description
        """
        degree = self.hgr.gr.degree[net]
        if degree < 2:  # unlikely, self-loop, etc.
            return  # does not provide any gain when move
        if degree > 3:
            self._init_gain_general_net(net, part)
        elif degree == 3:
            self._init_gain_3pin_net(net, part)
        else:  # degree == 2
            self._init_gain_2pin_net(net, part)

    def _modify_gain(self, v, pv, weight):
        """Modify gain

        Arguments:
            v (node_t):  description
            weight (int):  description
        """
        for k in self.RR.exclude(pv):
            self.vertex_list[k][v].data[0] += weight

    def _init_gain_2pin_net(self, net, part: Part):
        """initialize gain for 2-pin net

        Arguments:
            net (node_t):  description
            part (list):  description
        """
        netCur = iter(self.hgr.gr[net])
        w = next(netCur)
        v = next(netCur)
        part_w = part[w]
        part_v = part[v]
        weight = self.hgr.get_net_weight(net)
        if part_v == part_w:
            for a in [w, v]:
                self._modify_gain(a, part_v, -weight)
        else:
            self.totalcost += weight
            self.vertex_list[part_v][w].data[0] += weight
            self.vertex_list[part_w][v].data[0] += weight

    def _init_gain_3pin_net(self, net, part: Part):
        """initialize gain for 3-pin net

        Arguments:
            net (node_t):  description
            part (list):  description
        """
        netCur = iter(self.hgr.gr[net])
        w = next(netCur)
        v = next(netCur)
        u = next(netCur)
        part_w = part[w]
        part_v = part[v]
        part_u = part[u]
        weight = self.hgr.get_net_weight(net)
        if part_u == part_v:
            if part_w == part_v:
                for a in [u, v, w]:
                    self._modify_gain(a, part_v, -weight)
                return
            a, b, c = w, u, v
        elif part_w == part_v:
            a, b, c = u, v, w
        elif part_w == part_u:
            a, b, c = v, w, u
        else:
            self.totalcost += 2 * weight
            for a, b in permutations([u, v, w], 2):
                self.vertex_list[part[b]][a].data[0] += weight
            return

        self.vertex_list[part[b]][a].data[0] += weight
        for e in [b, c]:
            self._modify_gain(e, part[e], -weight)
            self.vertex_list[part[a]][e].data[0] += weight
        self.totalcost += weight

    def _init_gain_general_net(self, net, part: Part):
        """initialize gain for general net

        Arguments:
            net (node_t):  description
            part (list):  description
        """
        num = list(0 for _ in range(self.K))
        for w in self.hgr.gr[net]:
            num[part[w]] += 1

        weight = self.hgr.get_net_weight(net)

        for c in num:
            if c > 0:
                self.totalcost += weight
        self.totalcost -= weight

        for k, c in enumerate(num):
            if c == 0:
                for w in self.hgr.gr[net]:
                    self.vertex_list[k][w].data[0] -= weight
            elif c == 1:
                for w in self.hgr.gr[net]:
                    if part[w] == k:
                        self._modify_gain(w, part[w], weight)
                        break

    def update_move_init(self):
        """update move init"""
        self.deltaGainV = list(0 for _ in range(self.K))

    def update_move_2pin_net(self, part, move_info):
        """Update move for 2-pin net

        Arguments:
            part (list):  description
            move_info (MoveInfoV):  description

        Returns:
            dtype:  description
        """
        net, v, fromPart, toPart = move_info
        netCur = iter(self.hgr.gr[net])
        u = next(netCur)
        w = u if u != v else next(netCur)
        part_w = part[w]
        weight = self.hgr.get_net_weight(net)
        self.deltaGainW = list(0 for _ in range(self.K))

        for lPart in [fromPart, toPart]:
            if part_w == lPart:
                for k in range(self.K):  # cannot use zip here
                    self.deltaGainW[k] += weight
                    self.deltaGainV[k] += weight
            self.deltaGainW[lPart] -= weight
            weight = -weight

        return w

    def init_IdVec(self, v, net):
        self.IdVec = [w for w in self.hgr.gr[net] if w != v]
        # self.IdVec = []
        # for w in self.hgr.gr[net]:
        #     if w == v:
        #         continue
        #     self.IdVec.append(w)

    def update_move_3pin_net(self, part, move_info):
        """Update move for 3-pin net

        Arguments:
            part (list):  description
            move_info (MoveInfoV):  description

        Returns:
            dtype:  description
        """
        net, v, fromPart, toPart = move_info

        deltaGain = []
        degree = len(self.IdVec)
        deltaGain = list(list(0 for _ in range(self.K)) for _ in range(degree))

        weight = self.hgr.get_net_weight(net)

        l, u = fromPart, toPart

        part_w = part[self.IdVec[0]]
        part_u = part[self.IdVec[1]]

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
            return deltaGain

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

        return deltaGain

    def update_move_general_net(self, part, move_info):
        """Update move for general net

        Arguments:
            part (list):  description
            move_info (MoveInfoV):  description

        Returns:
            dtype:  description
        """
        net, v, fromPart, toPart = move_info
        num = list(0 for _ in range(self.K))
        # deltaGain = []
        # IdVec = []
        # for w in self.hgr.gr[net]:
        #     if w == v:
        #         continue
        #     num[part[w]] += 1
        #     IdVec.append(w)
        for w in self.IdVec:
            num[part[w]] += 1

        degree = len(self.IdVec)
        deltaGain = list(list(0 for _ in range(self.K)) for _ in range(degree))

        weight = self.hgr.get_net_weight(net)

        l, u = fromPart, toPart
        for _ in [0, 1]:
            if num[l] == 0:
                for index in range(degree):
                    deltaGain[index][l] -= weight
                if num[u] > 0:
                    for k in range(self.K):
                        self.deltaGainV[k] -= weight
            elif num[l] == 1:
                for index in range(degree):
                    part_w = part[self.IdVec[index]]
                    if part_w == l:
                        for k in range(self.K):
                            deltaGain[index][k] += weight
                        break
            weight = -weight
            l, u = u, l

        return deltaGain
