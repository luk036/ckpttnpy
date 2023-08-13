from typing import Any, Dict, List, Union

from .dllist import Dllink
from .lict import Lict

# from collections import Mapping

Part = Union[Dict[Any, int], List[int]]


class FMBiGainCalc:
    """The FMBiGainCalc class is used for calculating the bipartition gain."""

    __slots__ = ("totalcost", "hgr", "vertex_list", "idx_vec", "delta_gain_w")

    # public:

    def __init__(self, hgr, _: int = 2):  # num_parts == 2
        """Initialization
        The function initializes an object with a given Netlist and a default number of partitions, and
        creates a vertex list based on the type of modules in the Netlist.

        :param hgr: The `hgr` parameter is of type `Netlist` and represents a description of a netlist. It
        is used to initialize the `self.hgr` attribute of the class
        :param _: The parameter "_" is a placeholder variable that is not used in the code. It is common to
        use "_" as a variable name when you want to indicate that the value is not important or not used in
        the code. In this case, it is used as a placeholder for the second argument of the "__, defaults to
        2
        :type _: int (optional)
        """
        self.hgr = hgr
        if isinstance(self.hgr.modules, range):
            self.vertex_list = Lict([Dllink([0, i]) for i in self.hgr])
        elif isinstance(self.hgr.modules, list):
            self.vertex_list = {v: Dllink([0, v]) for v in self.hgr}
        else:
            raise NotImplementedError

    def init(self, part: Part) -> int:
        """
        The `init` function is used for (re)initializing the data and calculating the total cost for a given
        `part` in a graph.

        :param part: The `part` parameter is of type `Part`. It is used as an argument to the `init` method.
        The purpose of this parameter is not clear from the provided code snippet. It is likely that the
        `Part` class is defined elsewhere in the code and is used to represent some part
        :type part: Part
        :return: an integer value, which is the total cost.
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
        """
        The function `_init_gain` initializes the gain for a given network and partition.

        :param net: The `net` parameter represents a node in a graph. It is of type `node_t`
        :param part: The `part` parameter is a list that represents a partition of nodes in the network. It
        is used to determine the gain of moving a node from one partition to another
        :type part: Part
        :return: nothing.
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
        """
        The function `_modify_gain` modifies the gain of a vertex by adding a weight to its data.

        :param w: The parameter `w` represents a node in the graph. It is used to access a specific vertex
        in the `vertex_list` attribute of the class
        :param weight: The `weight` parameter is an integer that represents the weight to be added to the
        first element of the `data` attribute of the `w`-th element in the `vertex_list` list
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
        """
        The function initializes the gain for a 3-pin net based on the parts assigned to each pin.

        :param net: The `net` parameter is a `node_t` object, which represents a net in a circuit. It is
        used to identify a specific net in the circuit
        :param part: The `part` parameter is a list that represents the partitioning of nodes in the graph.
        Each element in the list corresponds to a node in the graph, and the value of the element indicates
        the partition to which the node belongs
        :type part: Part
        :return: Nothing is being returned. The function does not have a return statement.
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

    def _init_gain_general_net(self, net, part: Part) -> None:
        """
        The function `_init_gain_general_net` initializes the gain for a general net based on the number of
        connections to each partition.

        :param net: The `net` parameter is a node in a graph. It represents a general net in the context of
        the code
        :param part: The `part` parameter is a list that represents the partitioning of nodes in the
        network. Each element in the list corresponds to a node in the network, and the value of the element
        indicates which partition the node belongs to. For example, if `part = [0, 1,
        :type part: Part
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

    def update_move_init(self) -> None:
        """
        The function "update_move_init" does not perform any actions in the case of 2-way partitioning.
        """
        pass

    def update_move_2pin_net(self, part, move_info):
        """
        The function `update_move_2pin_net` updates the move for a 2-pin net by calculating the weight and
        delta gain.

        :param part: The `part` parameter is a list that represents the partitioning of the net. Each
        element in the list corresponds to a vertex in the net, and the value of the element indicates the
        partition to which the vertex belongs
        :param move_info: The `move_info` parameter is an instance of the `MoveInfoV` class. It contains
        information about the move being made for a 2-pin net. The attributes of the `MoveInfoV` class are:
        :return: the value of the variable "w".
        """
        net, v, from_part, _ = move_info
        net_cur = iter(self.hgr.gra[net])
        u = next(net_cur)
        w = u if u != v else next(net_cur)
        weight = self.hgr.get_net_weight(net)
        delta = 2 if part[w] == from_part else -2
        self.delta_gain_w = delta * weight
        return w

    def init_idx_vec(self, v, net) -> None:
        """
        The function `init_idx_vec` initializes the `idx_vec` attribute by filtering out the vertex `v` from
        the `gra[net]` list.

        :param v: The parameter `v` represents a vertex in the graph
        :param net: The `net` parameter represents a network or graph
        """
        self.idx_vec = [w for w in self.hgr.gra[net] if w != v]

    def update_move_3pin_net(self, part, move_info):
        """
        The function `update_move_3pin_net` updates the move for a 3-pin net by calculating the delta gain
        based on the current part assignment and the move information.

        :param part: A list that represents the partition of the net. It contains the indices of the parts
        that the net is currently connected to
        :param move_info: The `move_info` parameter is a tuple containing information about the move. It has
        the following structure:
        :return: a list of two elements, `delta_gain`.
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
        """
        The function `update_move_general_net` updates the move for a general net in a graph based on the
        given move information.

        :param part: A list that represents the partition of nodes in the network. Each element in the list
        corresponds to a node in the network and indicates which partition that node belongs to
        :param move_info: The `move_info` parameter is an instance of the `MoveInfoV` class. It contains
        information about the move being made in the general net
        :return: a list of delta gains.
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
