"""Gain calculator for FM bipartitioning.

FMBiGainCalc computes gains for moving vertices between two partitions (0/1).
Provides specialized initialization and update methods for 2-pin, 3-pin, and
general nets, tracking total cut cost.
"""

from typing import Any, Dict, List, Union

from mywheel.dllist import Dllink

Part = Union[Dict[Any, int], List[int]]


class FMBiGainCalc:
    """The FMBiGainCalc class is used for calculating the bipartition gain in
    Fiduccia-Mattheyses partitioning algorithm."""

    __slots__ = (
        "totalcost",
        "hyprgraph",
        "vertex_list",
        "vertex_nets",
        "net_pins",
        "net_degree",
        "idx_vec",
        "delta_gain_w",
        "_delta_gain_buf",
    )

    # public:

    def __init__(self, hyprgraph: Any, _: int = 2):  # num_parts == 2
        """Initialization
        The function initializes an object with a given Netlist and a default number
        of partitions, and creates a vertex list based on the type of modules in
        the Netlist.

        :param hyprgraph: The `hyprgraph` parameter is of type `Netlist` and
            represents a description of a netlist. It is used to initialize the
            `self.hyprgraph` attribute of the class

        Pre-allocates two reusable buffers:
        - ``idx_vec``: cleared and refilled by :meth:`init_idx_vec`
        - ``_delta_gain_buf``: grown as needed by :meth:`update_move_general_net`
        """
        self.hyprgraph = hyprgraph
        self.vertex_list: Any = None  # Will be set below
        if isinstance(self.hyprgraph.modules, range):
            self.vertex_list = [Dllink([0, i]) for i in self.hyprgraph]
        elif isinstance(self.hyprgraph.modules, list):
            self.vertex_list = {v: Dllink([0, v]) for v in self.hyprgraph}
        else:
            raise NotImplementedError
        self.net_pins = {
            net: list(self.hyprgraph.ugraph[net]) for net in self.hyprgraph.nets
        }
        self.net_degree = {net: len(pins) for net, pins in self.net_pins.items()}
        self.vertex_nets = {v: [] for v in self.hyprgraph}
        for net, pins in self.net_pins.items():
            for v in pins:
                self.vertex_nets[v].append(net)
        self.idx_vec: List[Any] = []
        self._delta_gain_buf: List[int] = []

    def init(self, part: Part) -> int:
        self.totalcost = 0
        vlist = self.vertex_list
        links = vlist if isinstance(vlist, list) else vlist.values()
        for vlink in links:
            vlink.data[0] = 0
        for net in self.hyprgraph.nets:
            self._init_gain(net, part)
        return self.totalcost

    # private:

    def _init_gain(self, net: Any, part: Part) -> None:
        degree = self.net_degree[net]
        if degree < 2:  # unlikely, self-loop, etc.
            return  # does not provide any gain when move
        if degree == 3:
            self._init_gain_3pin_net(net, part)
        elif degree == 2:
            self._init_gain_2pin_net(net, part)
        else:
            self._init_gain_general_net(net, part)

    def _modify_gain(self, w: Any, weight: int) -> None:
        self.vertex_list[w].data[0] += weight

    def _init_gain_2pin_net(self, net: Any, part: Part) -> None:
        w, v = self.net_pins[net]
        weight = self.hyprgraph.get_net_weight(net)
        if part[w] != part[v]:
            self.totalcost += weight
            self._modify_gain(w, weight)
            self._modify_gain(v, weight)
        else:
            self._modify_gain(w, -weight)
            self._modify_gain(v, -weight)

    def _init_gain_3pin_net(self, net: Any, part: Part) -> None:
        w, v, u = self.net_pins[net]
        weight = self.hyprgraph.get_net_weight(net)
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

    def _init_gain_general_net(self, net: Any, part: Part) -> None:
        pins = self.net_pins[net]
        num = [0, 0]
        for w in pins:
            num[part[w]] += 1

        weight = self.hyprgraph.get_net_weight(net)

        if num[0] > 0 and num[1] > 0:
            self.totalcost += weight

        for k in [0, 1]:
            if num[k] == 0:
                for w in pins:
                    self._modify_gain(w, -weight)
            elif num[k] == 1:
                for w in pins:
                    if part[w] == k:
                        self._modify_gain(w, weight)
                        break

    def update_move_init(self) -> None:
        """
        The function "update_move_init" does not perform any actions in the case of 2-way partitioning.
        """
        pass

    def update_move_2pin_net(self, part: Part, move_info: list) -> Any:
        """
        Updates the gain for a 2-pin net after a vertex move.

        :param part: Partition assignment for each vertex
        :param move_info: Tuple (net, v, from_part, to_part) for the moved vertex
        :return: The other vertex w connected to v via this net
        """
        net, v, from_part, _ = move_info
        pins = self.net_pins[net]
        u = pins[0]
        w = u if u != v else pins[1]
        weight = self.hyprgraph.get_net_weight(net)
        delta = 2 if part[w] == from_part else -2
        self.delta_gain_w = delta * weight
        return w

    def init_idx_vec(self, v: Any, net: Any) -> None:
        """Build ``self.idx_vec`` with all neighbours of *net* except *v*.

        Reuses the pre-allocated :attr:`idx_vec` list by clearing and
        refilling, avoiding allocation of a new list per call.

        :param v: Vertex being moved (excluded from the neighbour list).
        :param net: Net whose adjacency is iterated.
        """
        idx_vec = self.idx_vec
        idx_vec.clear()
        idx_vec.extend(self.net_pins[net])
        idx_vec.remove(v)

    def update_move_3pin_net(self, part: Part, move_info: list) -> List[int]:
        net, _, from_part, _ = move_info
        delta_gain = [0, 0]
        gain = self.hyprgraph.get_net_weight(net)

        part_w = part[self.idx_vec[0]]

        if part_w != from_part:
            gain = -gain

        if part_w == part[self.idx_vec[1]]:
            # .. svgbob::
            #
            #     "from"       "to"
            #   +----------+----------+
            #   | [w,x,v]|[]| [w,x]|[v]|
            #   +----------+----------+
            #
            # or (gain < 0)
            #
            #     "from"       "to"
            #   +----------+----------+
            #   | [w,x]|[v]| [w,x,v]|[]|
            #   +----------+----------+
            delta_gain[0] += gain
            delta_gain[1] += gain
        else:
            # .. svgbob::
            #
            #     "from"         "to"
            #   +------------+------------+
            #   | [w,v]|[x]  | [w]|[v,x]  |
            #   +------------+------------+
            #
            # or (gain < 0)
            #
            #     "from"         "to"
            #   +------------+------------+
            #   | [w]|[v,x]  | [w,v]|[x]  |
            #   +------------+------------+
            delta_gain[0] += gain
            delta_gain[1] -= gain

        return delta_gain

    def update_move_general_net(self, part: Part, move_info: list) -> List[int]:
        net, _, from_part, to_part = move_info
        num = [0, 0]
        for w in self.idx_vec:
            num[part[w]] += 1
        degree = len(self.idx_vec)
        delta_gain = self._delta_gain_buf
        if len(delta_gain) < degree:
            delta_gain.extend([0] * (degree - len(delta_gain)))
        # zero out first degree entries
        for i in range(degree):
            delta_gain[i] = 0
        gain = self.hyprgraph.get_net_weight(net)

        for l_part in [from_part, to_part]:
            if num[l_part] == 0:
                # .. svgbob::
                #
                #     "from"                "to"
                #   +-------------------+-----------------+
                #   | [w1,w2,...,v]|[] | [w1,w2,...]|[v] |
                #   +-------------------+-----------------+
                #
                for index in range(degree):
                    delta_gain[index] -= gain
                return delta_gain  # no need for further check
            elif num[l_part] == 1:
                # .. svgbob::
                #
                #     "from"                   "to"
                #   +----------------------+--------------------+
                #   | [w1,w2,...,v]|[w]   | [w1,w2,...]|[v,w]  |
                #   +----------------------+--------------------+
                #
                index = 0
                while part[self.idx_vec[index]] != l_part:
                    index += 1
                delta_gain[index] += gain
            gain = -gain

        return delta_gain
