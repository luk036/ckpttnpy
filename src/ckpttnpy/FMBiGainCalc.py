# -*- coding: utf-8 -*-

from typing import Any, Dict, List, Union

from .dllist import dllink

Part = Union[Dict[Any, int], List[int]]


class FMBiGainCalc:

    __slots__ = ('totalcost', 'H', 'vertex_list')

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
            self.vertex_list = [
                dllink(i) for i in self.H.modules
            ]
        elif isinstance(self.H.modules, list):
            self.vertex_list = {v: dllink(v) for v in self.H.modules}
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
                vlink.key = 0
        elif isinstance(self.H.modules, list):
            for vlink in self.vertex_list.values():
                vlink.key = 0
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
        self.vertex_list[w].key += weight

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
        IdVec = []
        for w in self.H.G[net]:
            num[part[w]] += 1
            IdVec.append(w)

        weight = self.H.get_net_weight(net)

        if num[0] > 0 and num[1] > 0:
            self.totalcost += weight

        for k in [0, 1]:
            if num[k] == 0:
                for w in IdVec:
                    self._modify_gain(w, -weight)
            elif num[k] == 1:
                for w in IdVec:
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
        return w, delta * weight

    def update_move_3pin_net(self, part, move_info):
        """Update move for 3-pin net

        Arguments:
            part (list):  description
            move_info (MoveInfoV):  description

        Returns:
            dtype:  description
        """
        net, v, fromPart, _ = move_info
        IdVec = []
        deltaGain = []
        for w in self.H.G[net]:
            if w == v:
                continue
            IdVec.append(w)

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
            part (list):  description
            move_info (MoveInfoV):  description

        Returns:
            dtype:  description
        """
        net, v, fromPart, toPart = move_info
        num = [0, 0]
        IdVec = []
        deltaGain = []
        for w in self.H.G[net]:
            if w == v:
                continue
            num[part[w]] += 1
            IdVec.append(w)

        degree = len(IdVec)
        deltaGain = list(0 for _ in range(degree))
        weight = self.H.get_net_weight(net)

        for l in [fromPart, toPart]:
            if num[l] == 0:
                for index in range(degree):
                    deltaGain[index] -= weight
                return IdVec, deltaGain
            elif num[l] == 1:
                for index in range(degree):
                    part_w = part[IdVec[index]]
                    if part_w == l:
                        deltaGain[index] += weight
                        break
            weight = -weight

        return IdVec, deltaGain
