"""Gain manager for FM bipartitioning.

FMGainMgr manages gain buckets used in the FM algorithm to select the best vertex
to move between partitions. Delegates actual gain calculation to a GainCalc instance.
Handles 2-pin, 3-pin, and general nets with specialized update methods.
"""

from abc import abstractmethod
from typing import Any, Dict, List, Union

from mywheel.bpqueue import BPQueue
from mywheel.dllist import Dllink, Dllist

Part = Union[Dict[Any, int], List[int]]

Item = Dllink[List[int]]


class FMGainMgr:
    """The `FMGainMgr` class is a base class for managing gains in Fiduccia-Mattheyses partitioning algorithm."""

    waitinglist = Dllist[List[int]]([0, 3734])

    # public:

    def __init__(self, GainCalc, hyprgraph, num_parts=2) -> None:
        """
        The function initializes an object with the given parameters and sets up variables for calculating
        gains.

        :param GainCalc: The `GainCalc` parameter is a type or class that is used for calculating the gain
            of a partition in the code. It is passed as an argument to the `__init__` method and stored as an
            instance variable `self.gain_calc`
        :param hyprgraph: The `hyprgraph` parameter is an object of type `Netlist`. It represents a netlist, which is a
            description of the connections between components in a circuit or system
        :param num_parts: The `num_parts` parameter is an integer that represents the number of partitions.
            It determines how many partitions the algorithm will divide the `hyprgraph` (Netlist) into, defaults to 2
            (optional)
        """
        self.hyprgraph = hyprgraph
        self.num_parts = num_parts
        self.gain_calc = GainCalc(hyprgraph, num_parts)
        self.pmax = self.hyprgraph.get_max_degree()
        bound = self.pmax * (num_parts - 1)
        self.gainbucket = [BPQueue(-bound, bound) for _ in range(num_parts)]

    def init(self, part) -> int:
        """
        The `init` function initializes the object and calculates the total cost based on the given part.

        :param part: A list that contains the description of a part
        :return: The total cost is being returned.
        """
        totalcost = self.gain_calc.init(part)
        self.waitinglist.clear()
        assert isinstance(totalcost, int)
        return totalcost

    def is_empty(self) -> bool:
        """
        The function `is_empty` checks if all the `_max` values of the `gainbucket` objects are equal to 0.
        :return: a boolean value.
        """
        return all(bckt._max == 0 for bckt in self.gainbucket)

    def select(self, part: Part) -> tuple[tuple[Any, int, int], int]:
        """
        The `select` function selects the best candidate based on the maximum gain and returns the move
        information and the maximum gain.

        :param part: The `part` parameter is a list that represents the current assignment of vertices to
            parts. Each element in the list corresponds to a vertex, and its value represents the part to which
            the vertex is currently assigned
        :return: a tuple containing the move_info_v and maxk values.
        """
        to_part = max(range(self.num_parts), key=lambda k: self.gainbucket[k].get_max())
        maxk = self.gainbucket[to_part].get_max()

        vlink = self.gainbucket[to_part].popleft()
        self.waitinglist.append(vlink)
        v = vlink.data[1]
        from_part = part[v]
        move_info_v = v, from_part, to_part
        return move_info_v, maxk

    def select_togo(self, to_part):
        """
        The function `select_togo` selects the best candidate to go based on the given `to_part` argument.

        :param to_part: The `to_part` parameter is of type `uint8_t` and represents a description
        :return: a tuple containing two values: `v` and `gainmax`.
        """
        gainmax = self.gainbucket[to_part].get_max()
        vlink = self.gainbucket[to_part].popleft()
        self.waitinglist.append(vlink)
        v = vlink.data[1]
        return v, gainmax

    def update_move(self, part, move_info_v):
        """
        The function `update_move` updates the gain of a move in a graph based on the given move
        information.

        :param part: A list that represents the partition of the graph. Each element in the list corresponds
            to a vertex in the graph and indicates which partition the vertex belongs to. For example, if part =
            [0, 1, 0, 1], it means that vertex 0 and vertex 2 belong
        :param move_info_v: The `move_info_v` parameter is a tuple that contains information about a move.
            It has the following structure:
        """
        self.gain_calc.update_move_init()
        v, from_part, to_part = move_info_v
        for net in self.hyprgraph.ugraph[v]:
            degree = self.hyprgraph.ugraph.degree[net]
            if degree < 2:  # unlikely, self-loop, etc.
                continue  # does not provide any gain change when move
            move_info = [net, v, from_part, to_part]
            if degree == 2:
                self._update_move_net(
                    part, move_info, self.gain_calc.update_move_2pin_net
                )
            else:
                self.gain_calc.init_idx_vec(v, net)
                if degree == 3:
                    self._update_move_net(
                        part, move_info, self.gain_calc.update_move_3pin_net
                    )
                else:
                    self._update_move_net(
                        part, move_info, self.gain_calc.update_move_general_net
                    )

    @abstractmethod
    def modify_key(self, w, part_w, key) -> None:
        """
        The `modify_key` function is an abstract method that takes in three arguments (`w`, `part_w`, and
        `key`) and does not return anything.

        :param w: A node_t object. It is a parameter of the modify_key method and is used in the
            implementation of the method
        :param part_w: The parameter `part_w` is of type `node_t`
        :param key: The `key` parameter is of type `int` or `int[]`. It represents a key that will be
            modified in some way
        """

    # private:

    def _update_move_net(self, part, move_info, gain_calc_method):
        """
        The function `_update_move_net` updates the move for a net in a partition solution.

        :param part: A list representing the partition solution. Each element in the list represents a node
            and its corresponding partition (0 or 1)
        :param move_info: The `move_info` parameter is a variable of type `type`. It is not clear what
            specific information is passed in this variable without further context
        :param gain_calc_method: The method to call on the gain_calc object.
        """
        delta_gain = gain_calc_method(part, move_info)
        if isinstance(delta_gain, (list, tuple)):
            for dGw, w in zip(delta_gain, self.gain_calc.idx_vec):
                self.modify_key(w, part[w], dGw)
        else:
            self.modify_key(delta_gain, part[delta_gain], self.gain_calc.delta_gain_w)
