# type: ignore

from itertools import permutations
from typing import Any, Dict, List, Union

from mywheel.dllist import Dllink
from mywheel.lict import Lict
from mywheel.robin import Robin

Part = Union[Dict[Any, int], List[int]]


class FMKWayGainCalc:
    """The `FMKWayGainCalc` class is used for calculating gain values in a hypergraph partitioning problem."""

    __slots__ = (
        "totalcost",
        "hyprgraph",
        "vertex_list",
        "num_parts",
        "rr",
        "delta_gain_v",
        "idx_vec",
        "delta_gain_w",
    )

    # public:

    def __init__(self, hyprgraph, num_parts: int) -> None:
        """
        The above function is an initialization function that sets up various variables and data structures
        for a graph partitioning algorithm.

        :param hyprgraph: The `hyprgraph` parameter is of type `Netlist` and represents a description of a netlist. It
        is used to store information about the modules and their connections in the netlist
        :param num_parts: The `num_parts` parameter is an integer that represents the number of partitions.
        It specifies how many partitions the algorithm should divide the given `hyprgraph` (Netlist) into
        :type num_parts: int
        """
        self.delta_gain_v = list()

        self.hyprgraph = hyprgraph
        self.num_parts = num_parts
        self.rr = Robin(num_parts)

        self.vertex_list = []

        if isinstance(self.hyprgraph.modules, range):
            self.vertex_list = [
                Lict([Dllink([0, i]) for i in self.hyprgraph]) for _ in range(num_parts)
            ]
        elif isinstance(self.hyprgraph.modules, list):
            self.vertex_list = [
                {v: Dllink([0, v]) for v in self.hyprgraph} for _ in range(num_parts)
            ]
        else:
            raise NotImplementedError

    def init(self, part: Part) -> None:
        """
        The `init` function initializes the total cost and resets the data values for each vertex link, and
        then initializes the gain for each net.

        :param part: The "part" parameter is a list that represents the partitioning of the graph. Each
        element in the list corresponds to a vertex in the graph, and the value of the element indicates
        which partition the vertex belongs to
        :type part: Part
        :return: The method is returning the value of the `totalcost` variable.
        """
        self.totalcost = 0
        for vlist in self.vertex_list:
            for vlink in vlist.values():
                vlink.data[0] = 0
        for net in self.hyprgraph.nets:
            self._init_gain(net, part)
        return self.totalcost

    def _init_gain(self, net, part: Part):
        """
        The function `_init_gain` initializes the gain for a given network based on its degree.

        :param net: The `net` parameter represents a node in a graph. It is of type `node_t`
        :param part: The `part` parameter is a list that represents a partition of nodes in the network. It
        is used to determine the gain of moving a particular node to a different partition
        :type part: Part
        :return: nothing.
        """
        degree = self.hyprgraph.gra.degree[net]
        if degree < 2:  # unlikely, self-loop, etc.
            return  # does not provide any gain when move
        if degree > 3:
            self._init_gain_general_net(net, part)
        elif degree == 3:
            self._init_gain_3pin_net(net, part)
        else:  # degree == 2
            self._init_gain_2pin_net(net, part)

    def _modify_gain(self, v, pv, weight):
        """
        The function `_modify_gain` modifies the gain of a node in a graph by adding a weight to it.

        :param v: The parameter `v` is of type `node_t` and represents a node in a graph. It is used as an
        argument in the function `_modify_gain`
        :param pv: pv is a node that is being excluded from the rr (round-robin) list
        :param weight: The weight parameter is an integer that represents the weight to be added to the data
        of each vertex in the vertex list
        """
        for k in self.rr.exclude(pv):
            self.vertex_list[k][v].data[0] += weight

    def _init_gain_2pin_net(self, net, part: Part):
        """
        The function `_init_gain_2pin_net` initializes the gain for a 2-pin net in a graph.

        :param net: The `net` parameter is a `node_t` object, which represents a net in a graph. It is used
        to identify a specific net in the graph
        :param part: The `part` parameter is a list that represents the partitioning of the nodes in the
        graph. Each element in the list corresponds to a node in the graph, and the value of the element
        indicates the partition to which the node belongs
        :type part: Part
        """
        net_cur = iter(self.hyprgraph.gra[net])
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

    def _init_gain_3pin_net(self, net, part: Part):
        """
        The function `_init_gain_3pin_net` initializes the gain for a 3-pin net in a graph.

        :param net: The `net` parameter represents a node in a graph. It is of type `node_t`
        :param part: The `part` parameter is a list that represents the partitioning of nodes in the graph.
        Each element in the list corresponds to a node in the graph, and the value of the element represents
        the partition that the node belongs to
        :type part: Part
        :return: The function does not explicitly return anything.
        """
        net_cur = iter(self.hyprgraph.gra[net])
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

    def _init_gain_general_net(self, net, part: Part):
        """
        The function `_init_gain_general_net` initializes the gain for a general net based on the number of
        connections to each partition.

        :param net: The `net` parameter is a node in a graph. It represents a general net in the context of
        the code
        :param part: The `part` parameter is a list that represents the partitioning of nodes in the
        network. Each element in the list corresponds to a node in the network, and the value of the element
        represents the partition to which the node belongs
        :type part: Part
        """
        num = [0] * self.num_parts
        for w in self.hyprgraph.gra[net]:
            num[part[w]] += 1

        weight = self.hyprgraph.get_net_weight(net)

        for c in num:
            if c > 0:
                self.totalcost += weight
        self.totalcost -= weight

        for k, c in enumerate(num):
            if c == 0:
                for w in self.hyprgraph.gra[net]:
                    self.vertex_list[k][w].data[0] -= weight
            elif c == 1:
                for w in self.hyprgraph.gra[net]:
                    if part[w] == k:
                        self._modify_gain(w, part[w], weight)
                        break

    def update_move_init(self):
        """
        The function "update_move_init" initializes a list called "delta_gain_v" with zeros.
        """
        self.delta_gain_v = [0] * self.num_parts

    def update_move_2pin_net(self, part, move_info):
        """Update move for 2-pin net

        The function `update_move_2pin_net` updates the move for a 2-pin net in a graph.

        :param part: A list that represents the partitioning of the circuit. Each element in the list
        corresponds to a vertex in the circuit graph and indicates which partition the vertex belongs to
        :param move_info: The `move_info` parameter is a tuple containing four elements: `net`, `v`,
        `from_part`, and `to_part`
        :return: the value of the variable "w".
        """
        net, v, from_part, to_part = move_info
        net_cur = iter(self.hyprgraph.gra[net])
        u = next(net_cur)
        w = u if u != v else next(net_cur)
        part_w = part[w]
        weight = self.hyprgraph.get_net_weight(net)
        self.delta_gain_w = [0] * self.num_parts

        for l_part in [from_part, to_part]:
            if part_w == l_part:
                for k in range(self.num_parts):  # cannot use zip here
                    self.delta_gain_w[k] += weight
                    self.delta_gain_v[k] += weight
            self.delta_gain_w[l_part] -= weight
            weight = -weight

        return w

    def init_idx_vec(self, v, net):
        """
        The function `init_idx_vec` initializes the `idx_vec` attribute by creating a list of all elements
        in `self.hyprgraph.gra[net]` except for `v`.

        :param v: The parameter `v` represents a vertex in the graph `net`
        :param net: The parameter "net" is a variable that represents a network or graph
        """
        self.idx_vec = [w for w in self.hyprgraph.gra[net] if w != v]

    def update_move_3pin_net(self, part, move_info):
        """Update move for 3-pin net

        The function `update_move_3pin_net` updates the move for a 3-pin net in a graph.

        :param part: A list representing the partition of the net. Each element in the list corresponds to a
        pin in the net and indicates which part of the partition the pin belongs to
        :param move_info: The `move_info` parameter is a tuple containing information about the move. It has
        the following structure:
        :return: the variable `delta_gain`, which is a list of lists.
        """
        net, _, from_part, to_part = move_info

        delta_gain = []
        degree = len(self.idx_vec)
        delta_gain = list([0] * self.num_parts for _ in range(degree))

        weight = self.hyprgraph.get_net_weight(net)

        l, u = from_part, to_part

        part_w = part[self.idx_vec[0]]
        part_u = part[self.idx_vec[1]]

        if part_w == part_u:
            for _ in [0, 1]:
                if part_w != l:
                    delta_gain[0][l] -= weight
                    delta_gain[1][l] -= weight
                    if part_w == u:
                        for k in range(self.num_parts):
                            self.delta_gain_v[k] -= weight
                weight = -weight
                l, u = u, l
            return delta_gain

        for _ in [0, 1]:
            if part_w == l:
                for k in range(self.num_parts):
                    delta_gain[0][k] += weight
            elif part_u == l:
                for k in range(self.num_parts):
                    delta_gain[1][k] += weight
            else:
                delta_gain[0][l] -= weight
                delta_gain[1][l] -= weight
                if part_w == u or part_u == u:
                    for k in range(self.num_parts):
                        self.delta_gain_v[k] -= weight
            weight = -weight
            l, u = u, l

        return delta_gain

    def update_move_general_net(self, part, move_info):
        """Update move for general net

        The function `update_move_general_net` updates the move for a general net in a graph partitioning
        algorithm.

        :param part: A list that represents the partition of the nodes in the network. Each element in the
        list corresponds to a node and indicates which part of the network the node belongs to
        :param move_info: The `move_info` parameter is an instance of the `MoveInfoV` class. It contains
        information about the move being made in the general net. The `move_info` object has the following
        attributes:
        :return: the variable "delta_gain", which is a list of lists.
        """
        net, _, from_part, to_part = move_info
        num = [0] * self.num_parts
        for w in self.idx_vec:
            num[part[w]] += 1

        degree = len(self.idx_vec)
        delta_gain = list([0] * self.num_parts for _ in range(degree))

        weight = self.hyprgraph.get_net_weight(net)

        l, u = from_part, to_part
        for _ in [0, 1]:
            if num[l] == 0:
                for index in range(degree):
                    delta_gain[index][l] -= weight
                if num[u] > 0:
                    for k in range(self.num_parts):
                        self.delta_gain_v[k] -= weight
            elif num[l] == 1:
                index = 0
                while True:
                    part_w = part[self.idx_vec[index]]
                    if part_w == l:
                        for k in range(self.num_parts):
                            delta_gain[index][k] += weight
                        break
                    index += 1
            weight = -weight
            l, u = u, l

        return delta_gain
