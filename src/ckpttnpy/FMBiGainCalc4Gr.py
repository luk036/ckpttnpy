# -*- coding: utf-8 -*-

from typing import Any, Dict, List, Union

from .dllist import dllink

Part = Union[Dict[Any, int], List[int]]


class FMBiGainCalc4Gr:

    __slots__ = ('totalcost', 'H', 'vertex_list', 'IdVec', 'deltaGainW')

    # public:

    def __init__(self, H, K=2):
        """Initialization

        Arguments:
            H (Netlist):  description

        Keyword Arguments:
            K (uint8_t):  number of partitions (default: {2})
        """
        self.H = H
        self.vertex_list = {v: dllink([0, v]) for v in self.H}

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
        for vlink in self.vertex_list.values():
            vlink.data[0] = 0

        for e in self.H.edges():
            # for net in self.H.net_list:
            self._init_gain(e, part)
        return self.totalcost

    # private:

    def _init_gain(self, e, part: Part):
        """initialize gain

        Arguments:
            net (node_t):  description
            part (list):  description
        """
        u, v = e
        if u == v:  # unlikely, self-loop, etc.
            return  # does not provide any gain when move
        self._init_gain_2pin_net(e, part)

    def _modify_gain(self, w, weight):
        """Modify gain

        Arguments:
            v (node_t):  description
            weight (int):  description
        """
        self.vertex_list[w].data[0] += weight

    def _init_gain_2pin_net(self, e, part: Part):
        """initialize gain for 2-pin net

        Arguments:
            net (node_t):  description
            part (list):  description
        """
        w, v = e
        weight = self.H.get_net_weight(e)
        if part[w] != part[v]:
            self.totalcost += weight
            self._modify_gain(w, weight)
            self._modify_gain(v, weight)
        else:
            self._modify_gain(w, -weight)
            self._modify_gain(v, -weight)

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
        e, v, fromPart, _ = move_info
        u, u2 = e
        w = u if u != v else u2
        weight = self.H.get_net_weight(e)
        delta = 2 if part[w] == fromPart else -2
        self.deltaGainW = delta * weight
        return w
