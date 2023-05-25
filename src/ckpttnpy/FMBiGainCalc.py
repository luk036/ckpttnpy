from .dllist import Dllink
from .lict import Lict

from typing import Any, Dict, List, Union

# from collections import Mapping

Part = Union[Dict[Any, int], List[int]]


class FMBiGainCalc:
    __slots__ = ("totalcost", "hgr", "vertex_list", "idx_vec", "delta_gain_w")

    # public:

    def __init__(self, hgr, _: int = 2):  # num_parts == 2
        """Initialization

        Arguments:
            hgr (Netlist):  description

        Keyword Arguments:
            num_parts (uint8_t):  number of partitions (default: {2})
        """
        self.hgr = hgr
        if isinstance(self.hgr.modules, range):
            self.vertex_list = Lict([Dllink([0, i]) for i in self.hgr])
        elif isinstance(self.hgr.modules, list):
            self.vertex_list = {v: Dllink([0, v]) for v in self.hgr}
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
        for vlink in self.vertex_list.values():
            vlink.data[0] = 0
        for net in self.hgr.nets:
            # for net in self.hgr.net_list:
            self._init_gain(net, part)
        return self.totalcost

    # private:

    def _init_gain(self, net, part: Part):
        """initialize gain

        Arguments:
            net (node_t):  description
            part (list):  description
        """
        degree = self.hgr.gra.degree[net]
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
        net_cur = iter(self.hgr.gra[net])
        w = next(net_cur)
        v = next(net_cur)
        weight = self.hgr.get_net_weight(net)
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
        net_cur = iter(self.hgr.gra[net])
        w = next(net_cur)
        v = next(net_cur)
        u = next(net_cur)
        weight = self.hgr.get_net_weight(net)
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
        for w in self.hgr.gra[net]:
            num[part[w]] += 1

        weight = self.hgr.get_net_weight(net)

        if num[0] > 0 and num[1] > 0:
            self.totalcost += weight

        for k in [0, 1]:
            if num[k] == 0:
                for w in self.hgr.gra[net]:
                    self._modify_gain(w, -weight)
            elif num[k] == 1:
                for w in self.hgr.gra[net]:
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
        net, v, from_part, _ = move_info
        net_cur = iter(self.hgr.gra[net])
        u = next(net_cur)
        w = u if u != v else next(net_cur)
        weight = self.hgr.get_net_weight(net)
        delta = 2 if part[w] == from_part else -2
        self.delta_gain_w = delta * weight
        return w

    def init_idx_vec(self, v, net):
        self.idx_vec = [w for w in self.hgr.gra[net] if w != v]
        # for w in filter(lambda w: w != v, self.hgr.gra[net]):
        #     self.idx_vec.append(w)

    def update_move_3pin_net(self, part, move_info):
        """Update move for 3-pin net

        Arguments:
            part (list):  description
            move_info (MoveInfoV):  description

        Returns:
            dtype:  description
        """
        net, _, from_part, _ = move_info
        delta_gain = [0, 0]
        gain = self.hgr.get_net_weight(net)

        part_w = part[self.idx_vec[0]]

        if part_w != from_part:
            gain = -gain

        if part_w == part[self.idx_vec[1]]:
            # from: [w, x, v] | []
            # to: [w, x] | [v]
            # or (gain < 0)
            # from: [w, x] | [v]
            # to: [w, x, v] | []
            delta_gain[0] += gain
            delta_gain[1] += gain
        else:
            # from: [w, v] | [x]
            # to: [w] | [v, x]
            # or (gain < 0)
            # from: [w] | [v, x]
            # to: [w, v] | [x]
            delta_gain[0] += gain
            delta_gain[1] -= gain

        return delta_gain

    def update_move_general_net(self, part, move_info):
        """Update move for general net

        Arguments:
            part (list):  description
            move_info (MoveInfoV):  description

        Returns:
            dtype:  description
        """
        net, _, from_part, to_part = move_info
        num = [0, 0]
        for w in self.idx_vec:
            num[part[w]] += 1
        degree = len(self.idx_vec)
        delta_gain = [0] * degree
        gain = self.hgr.get_net_weight(net)

        for l_part in [from_part, to_part]:
            if num[l_part] == 0:
                # from: [w1, w2, w3 ..., v] | []
                # to: [w1, w2, w3 ... ] | [v]
                for index in range(degree):
                    delta_gain[index] -= gain
                return delta_gain
            elif num[l_part] == 1:
                # from: [w1, w2, w3 ..., v] | [w]
                # to: [w1, w2, w3 ... ] | [v, w]
                for index in range(degree):
                    part_w = part[self.idx_vec[index]]
                    if part_w == l_part:
                        delta_gain[index] += gain
                        break
            gain = -gain

        return delta_gain
