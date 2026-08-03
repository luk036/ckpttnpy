"""Gain calculator for FM k-way partitioning.

FMKWayGainCalc computes per-partition gains for moving vertices in k-way
partitioning. Maintains a separate vertex list per partition and provides
specialized init/update for 2-pin, 3-pin, and general nets.
"""

from itertools import permutations
from typing import Any, Dict, List, Union

from mywheel.dllist import Dllink
from mywheel.map_adapter import MapAdapter
from mywheel.robin import Robin

Part = Union[Dict[Any, int], List[int]]


class FMKWayGainCalc:
    """The `FMKWayGainCalc` class is used for calculating gain values in Fiduccia-Mattheyses partitioning algorithm."""

    __slots__ = (
        "totalcost",
        "hyprgraph",
        "vertex_list",
        "num_parts",
        "rr",
        "delta_gain_v",
        "idx_vec",
        "delta_gain_w",
        "_delta_gain_pool",
        "_num_pool",
    )

    # public:

    def __init__(self, hyprgraph: Any, num_parts: int) -> None:
        """
        The above function is an initialization function that sets up various variables and data structures
        for a graph partitioning algorithm.

        :param hyprgraph: The `hyprgraph` parameter is of type `Netlist` and represents a description of a netlist. It
            is used to store information about the modules and their connections in the netlist
        :param num_parts: The `num_parts` parameter is an integer that represents the number of partitions.
            It specifies how many partitions the algorithm should divide the given `hyprgraph` (Netlist) into
        :type num_parts: int

        Pre-allocates several reusable buffers:
        - ``delta_gain_v``, ``delta_gain_w``: zeroed per-call via re-zeroing
        - ``idx_vec``: cleared and refilled by :meth:`init_idx_vec`
        - ``_delta_gain_pool``: grown as needed by :meth:`_alloc_delta`
        - ``_num_pool``: reused by :meth:`_init_gain_general_net` and
          :meth:`update_move_general_net`
        """
        self.delta_gain_v: List[int] = [0] * num_parts
        self.delta_gain_w: List[int] = [0] * num_parts

        self.hyprgraph = hyprgraph
        self.num_parts = num_parts
        self.rr = Robin(num_parts)
        self.vertex_list: Any = None  # Will be set below

        if isinstance(self.hyprgraph.modules, range):
            self.vertex_list = [
                MapAdapter([Dllink([0, i]) for i in self.hyprgraph])
                for _ in range(num_parts)
            ]
        elif isinstance(self.hyprgraph.modules, list):
            self.vertex_list = [
                {v: Dllink([0, v]) for v in self.hyprgraph} for _ in range(num_parts)
            ]
        else:
            raise NotImplementedError
        self.idx_vec: List[Any] = []
        self._delta_gain_pool: List[List[int]] = []
        self._num_pool: List[int] = [0] * num_parts

    def init(self, part: Part) -> int:

        self.totalcost = 0
        for vlist in self.vertex_list:
            for vlink in vlist.values():
                vlink.data[0] = 0
        for net in self.hyprgraph.nets:
            self._init_gain(net, part)
        return self.totalcost

    def _init_gain(self, net: Any, part: Part) -> None:

        degree = self.hyprgraph.ugraph.degree[net]
        if degree < 2:  # unlikely, self-loop, etc.
            return  # does not provide any gain when move
        if degree > 3:
            self._init_gain_general_net(net, part)
        elif degree == 3:
            self._init_gain_3pin_net(net, part)
        else:  # degree == 2
            self._init_gain_2pin_net(net, part)

    def _modify_gain(self, v: Any, pv: int, weight: int) -> None:

        for k in self.rr.exclude(pv):
            self.vertex_list[k][v].data[0] += weight

    def _init_gain_2pin_net(self, net: Any, part: Part) -> None:

        net_cur = iter(self.hyprgraph.ugraph[net])
        w = next(net_cur)
        v = next(net_cur)
        part_w = part[w]
        part_v = part[v]
        weight = self.hyprgraph.get_net_weight(net)
        if part_v == part_w:
            for a in [w, v]:
                self._modify_gain(a, part_v, -weight)
        else:
            self.totalcost += weight
            self.vertex_list[part_v][w].data[0] += weight
            self.vertex_list[part_w][v].data[0] += weight

    def _init_gain_3pin_net(self, net: Any, part: Part) -> None:

        net_cur = iter(self.hyprgraph.ugraph[net])
        w = next(net_cur)
        v = next(net_cur)
        u = next(net_cur)
        part_w = part[w]
        part_v = part[v]
        part_u = part[u]
        weight = self.hyprgraph.get_net_weight(net)
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

    def _init_gain_general_net(self, net: Any, part: Part) -> None:
        """Initialize gain for a general net using per-partition counts.

        Reuses :attr:`_num_pool` instead of allocating a new ``[0] * num_parts``.

        For partitions with 0 vertices in the net, all connected vertices get
        negative gain.  For partitions with exactly 1 vertex, that vertex gets
        positive gain.

        :param net: Net node in the hypergraph
        :param part: Partition assignment for each vertex
        """
        num = self._num_pool
        for k in range(self.num_parts):
            num[k] = 0
        for w in self.hyprgraph.ugraph[net]:
            num[part[w]] += 1

        weight = self.hyprgraph.get_net_weight(net)

        for c in num:
            if c > 0:
                self.totalcost += weight
        self.totalcost -= weight

        for k, c in enumerate(num):
            if c == 0:
                for w in self.hyprgraph.ugraph[net]:
                    self.vertex_list[k][w].data[0] -= weight
            elif c == 1:
                cur = iter(self.hyprgraph.ugraph[net])
                w = next(cur)
                while part[w] != k:
                    w = next(cur)
                self._modify_gain(w, part[w], weight)

    def update_move_init(self) -> None:
        """Zero out the per-partition ``delta_gain_v`` buffer.

        Called once per vertex move, before processing each affected net.
        Reuses the existing list instead of allocating a new ``[0] * N``.
        """
        for k in range(self.num_parts):
            self.delta_gain_v[k] = 0

    def update_move_2pin_net(self, part: Part, move_info: list) -> Any:
        """Update gains for a 2-pin net after a vertex move.

        Reuses the pre-allocated :attr:`delta_gain_w` list by re-zeroing
        entries instead of allocating a new ``[0] * num_parts``.

        :param part: Current partition assignment for each vertex
        :param move_info: Tuple (net, v, from_part, to_part) for the moved vertex
        :return: The other vertex w connected to v via this net
        """
        net, v, from_part, to_part = move_info
        net_cur = iter(self.hyprgraph.ugraph[net])
        u = next(net_cur)
        w = u if u != v else next(net_cur)
        part_w = part[w]
        weight = self.hyprgraph.get_net_weight(net)
        delta_gain_w = self.delta_gain_w
        for k in range(self.num_parts):
            delta_gain_w[k] = 0

        for l_part in [from_part, to_part]:
            if part_w == l_part:
                for k in range(self.num_parts):  # cannot use zip here
                    self.delta_gain_w[k] += weight
                    self.delta_gain_v[k] += weight
            self.delta_gain_w[l_part] -= weight
            weight = -weight

        return w

    def init_idx_vec(self, v: Any, net: Any) -> None:
        """Build ``self.idx_vec`` with all neighbours of *net* except *v*.

        Reuses the pre-allocated :attr:`idx_vec` list by clearing and
        refilling, avoiding allocation of a new list per call.

        :param v: Vertex being moved (excluded from the neighbour list).
        :param net: Net whose adjacency is iterated.
        """
        self.idx_vec.clear()
        for w in self.hyprgraph.ugraph[net]:
            if w != v:
                self.idx_vec.append(w)

    def _alloc_delta(self, degree: int) -> List[List[int]]:
        """Return a ``degree × num_parts`` zeroed list from a reusable pool.

        The pool grows on demand and is never shrunk, avoiding repeated
        allocations of inner lists for every call to the 3-pin or general
        net update methods.

        :param degree: Number of outer rows requested.
        :returns: A slice of the pool, zeroed to ``degree × num_parts``.
        """
        pool = self._delta_gain_pool
        while len(pool) < degree:
            pool.append([0] * self.num_parts)
        # zero out the rows we need
        for i in range(degree):
            row = pool[i]
            for k in range(self.num_parts):
                row[k] = 0
        return pool[:degree]

    def update_move_3pin_net(self, part: Part, move_info: list) -> List[List[int]]:
        """Update gains for a 3-pin net after a vertex move.

        Uses :meth:`_alloc_delta` to obtain a zeroed ``degree × num_parts``
        matrix from the reusable pool rather than allocating new inner lists.

        :param part: Current partition assignment for each vertex
        :param move_info: Tuple (net, v, from_part, to_part) for the moved vertex
        :return: delta_gain list (one per remaining vertex, each a list of per-partition gains)
        """
        net, _, from_part, to_part = move_info
        degree = len(self.idx_vec)
        delta_gain = self._alloc_delta(degree)
        weight = self.hyprgraph.get_net_weight(net)
        fp, tp = from_part, to_part
        part_w = part[self.idx_vec[0]]
        part_u = part[self.idx_vec[1]]

        if part_w == part_u:
            for _ in [0, 1]:
                if part_w != fp:
                    delta_gain[0][fp] -= weight
                    delta_gain[1][fp] -= weight
                    if part_w == tp:
                        for k in range(self.num_parts):
                            self.delta_gain_v[k] -= weight
                weight = -weight
                fp, tp = tp, fp
            return delta_gain

        for _ in [0, 1]:
            if part_w == fp:
                for k in range(self.num_parts):
                    delta_gain[0][k] += weight
            elif part_u == fp:
                for k in range(self.num_parts):
                    delta_gain[1][k] += weight
            else:
                delta_gain[0][fp] -= weight
                delta_gain[1][fp] -= weight
                if part_w == tp or part_u == tp:
                    for k in range(self.num_parts):
                        self.delta_gain_v[k] -= weight
            weight = -weight
            fp, tp = tp, fp

        return delta_gain

    def update_move_general_net(self, part: Part, move_info: list) -> List[List[int]]:
        """Update gains for a general (degree > 3) net after a vertex move.

        Uses :meth:`_alloc_delta` and reuses :attr:`_num_pool` to avoid
        allocating new lists on each call.

        :param part: Current partition assignment for each vertex
        :param move_info: Tuple (net, v, from_part, to_part) for the moved vertex
        :return: delta_gain list (one per remaining vertex, each a list of per-partition gains)
        """
        net, _, from_part, to_part = move_info
        num = self._num_pool
        for k in range(self.num_parts):
            num[k] = 0
        for w in self.idx_vec:
            num[part[w]] += 1

        degree = len(self.idx_vec)
        delta_gain = self._alloc_delta(degree)
        weight = self.hyprgraph.get_net_weight(net)

        fp, tp = from_part, to_part
        for _ in [0, 1]:
            if num[fp] == 0:
                for index in range(degree):
                    delta_gain[index][fp] -= weight
                if num[tp] > 0:
                    for k in range(self.num_parts):
                        self.delta_gain_v[k] -= weight
            elif num[fp] == 1:
                index = 0
                while part[self.idx_vec[index]] != fp:
                    index += 1
                for k in range(self.num_parts):
                    delta_gain[index][k] += weight
            weight = -weight
            fp, tp = tp, fp

        return delta_gain
