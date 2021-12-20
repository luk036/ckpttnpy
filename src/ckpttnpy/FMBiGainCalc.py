# -*- coding: utf-8 -*-

from typing import Any, Dict, List, Union

from .dllist import dllink

Part = Union[Dict[Any, int], List[int]]


class FMBiGainCalc:

    __slots__ = ("totalcost", "H", "vertex_list", "IdVec", "deltaGainW")

    # public:

    def __init__(self, H, K=2):
        """Initialization

        Arguments:
            H (Netlist):  description

        Keyword Arguments:
            K (uint8_t):  number of partitions (default: {2})
        """
        self.H = H
        if isinstance(self.H.modules, range):
            self.vertex_list = [dllink([0, i]) for i in self.H]
        elif isinstance(self.H.modules, list):
            self.vertex_list = {v: dllink([0, v]) for v in self.H}
        else:
            raise NotImplementedError

    def init(self, part: Part) -> int:
        """(re)initialization after creation

        Arguments:
            part ([type]): [description]

        Raises:
            NotImplementedError: [description]

        Returns:
            [type]: [description]
        """
        self.totalcost = 0
        if isinstance(self.H.modules, range):
            for vlink in self.vertex_list:
                vlink.data[0] = 0
        elif isinstance(self.H.modules, list):
            for vlink in self.vertex_list.values():
                vlink.data[0] = 0
        else:
            raise NotImplementedError

        for net in self.H.nets:
            # for net in self.H.net_list:
            self._init_gain(net, part)
        return self.totalcost

    # private:

    def _init_gain(self, net, part: Part):
        """initialize gain

        Arguments:
            net (node_t):  description
            part (list):  description
        """
        degree = self.H.G.degree[net]
        if degree < 2:  # unlikely, self-loop, etc.
            return  # does not provide any gain when move
        if degree == 3:
            self._init_gain_3pin_net(net, part)
        elif degree == 2:
            self._init_gain_2pin_net(net, part)
        else:
            self._init_gain_general_net(net, part)

    def _modify_gain(self, w, weight):
        """Modify gain

        Arguments:
            v (node_t):  description
            weight (int):  description
        """
        self.vertex_list[w].data[0] += weight

    def _init_gain_2pin_net(self, net, part: Part):
        """initialize gain for 2-pin net

        Arguments:
            net (node_t):  description
            part (list):  description
        """
        netCur = iter(self.H.G[net])
        w = next(netCur)
        v = next(netCur)
        weight = self.H.get_net_weight(net)
        if part[w] != part[v]:
            self.totalcost += weight
            self._modify_gain(w, weight)
            self._modify_gain(v, weight)
        else:
            self._modify_gain(w, -weight)
            self._modify_gain(v, -weight)

    def _init_gain_3pin_net(self, net, part: Part):
        """initialize gain for 3-pin net

        Arguments:
            net (node_t):  description
            part (list):  description
        """
        netCur = iter(self.H.G[net])
        w = next(netCur)
        v = next(netCur)
        u = next(netCur)
        weight = self.H.get_net_weight(net)
        if part[u] == part[v]:
            if part[w] == part[v]:
                for a in [u, v, w]:
                    self._modify_gain(a, -weight)
                return
            self._modify_gain(w, weight)
        elif part[w] == part[v]:
            self._modify_gain(u, weight)
        else:  # part[u] == part[w]
            self._modify_gain(v, weight)
        self.totalcost += weight

    def _init_gain_general_net(self, net, part: Part):
        """initialize gain for general net

        Arguments:
            net (node_t):  description
            part (list):  description
        """
        num = [0, 0]
        for w in self.H.G[net]:
            num[part[w]] += 1

        weight = self.H.get_net_weight(net)

        if num[0] > 0 and num[1] > 0:
            self.totalcost += weight

        for k in [0, 1]:
            if num[k] == 0:
                for w in self.H.G[net]:
                    self._modify_gain(w, -weight)
            elif num[k] == 1:
                for w in self.H.G[net]:
                    if part[w] == k:
                        self._modify_gain(w, weight)
                        break

    def update_move_init(self):
        """update move init

        nothing to do in 2-way partitioning
        """
        pass

    def update_move_2pin_net(self, part, move_info):
        """Update move for 2-pin net

        Arguments:
            part (list):  description
            move_info (MoveInfoV):  description

        Returns:
            dtype:  description
        """
        net, v, fromPart, _ = move_info
        netCur = iter(self.H.G[net])
        u = next(netCur)
        w = u if u != v else next(netCur)
        weight = self.H.get_net_weight(net)
        delta = 2 if part[w] == fromPart else -2
        self.deltaGainW = delta * weight
        return w

    def init_IdVec(self, v, net):
        self.IdVec = [w for w in self.H.G[net] if w != v]
        # for w in filter(lambda w: w != v, self.H.G[net]):
        #     self.IdVec.append(w)

    def update_move_3pin_net(self, part, move_info):
        """Update move for 3-pin net

        Arguments:
            part (list):  description
            move_info (MoveInfoV):  description

        Returns:
            dtype:  description
        """
        net, v, fromPart, _ = move_info
        deltaGain = []
        # IdVec = []
        # for w in self.H.G[net]:
        #     if w == v:
        #         continue
        #     IdVec.append(w)

        deltaGain = [0, 0]
        weight = self.H.get_net_weight(net)

        part_w = part[self.IdVec[0]]

        if part_w != fromPart:
            weight = -weight

        if part_w == part[self.IdVec[1]]:
            deltaGain[0] += weight
            deltaGain[1] += weight
        else:
            deltaGain[0] += weight
            deltaGain[1] -= weight

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
        # deltaGain = []
        # IdVec = []
        # for w in self.H.G[net]:
        #     if w == v:
        #         continue
        #     num[part[w]] += 1
        #     IdVec.append(w)
        num = [0, 0]
        for w in self.IdVec:
            num[part[w]] += 1
        degree = len(self.IdVec)
        deltaGain = list(0 for _ in range(degree))
        weight = self.H.get_net_weight(net)

        for lPart in [fromPart, toPart]:
            if num[lPart] == 0:
                for index in range(degree):
                    deltaGain[index] -= weight
                return deltaGain
            elif num[lPart] == 1:
                for index in range(degree):
                    part_w = part[self.IdVec[index]]
                    if part_w == lPart:
                        deltaGain[index] += weight
                        break
            weight = -weight

        return deltaGain
