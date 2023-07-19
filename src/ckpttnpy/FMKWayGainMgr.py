# -*- coding: utf-8 -*-

from typing import Any, Dict, List, Union

from .FMGainMgr import FMGainMgr
from .robin import Robin

Part = Union[Dict[Any, int], List[int]]


class FMKWayGainMgr(FMGainMgr):
    """The `FMKWayGainMgr` class is a subclass of `FMGainMgr` that initializes with a `GainCalc` object, a
    `Netlist` object, and a number of partitions, and also has a `Robin` object.
    """

    # public:

    def __init__(self, GainCalc, hgr, num_parts: int):
        """
        The function initializes an object with the given parameters and calls the parent class's
        initialization method.

        :param GainCalc: The `GainCalc` parameter is a type or class that is used for calculating the gain
        of a netlist. It is likely a separate class that has methods or functions for calculating the gain
        based on certain criteria or algorithms
        :param hgr: The `hgr` parameter is of type `Netlist` and it represents a description of the netlist
        :param num_parts: The `num_parts` parameter is an integer that represents the number of partitions.
        It is of type `int`
        :type num_parts: int
        """
        FMGainMgr.__init__(self, GainCalc, hgr, num_parts)
        self.rr = Robin(num_parts)

    def init(self, part: Part):
        """
        The `init` function initializes or reinitializes certain variables and data structures based on the
        given `part` argument.

        :param part: The `part` parameter is a list that represents the parts in the system. Each element in
        the list corresponds to a part, and the index of the element represents the part number
        :type part: Part
        :return: The variable `totalcost` is being returned.
        """
        totalcost = FMGainMgr.init(self, part)

        for bckt in self.gainbucket:
            bckt.clear()

        for v in self.hgr:
            pv = part[v]
            for k in self.rr.exclude(pv):
                vlink = self.gain_calc.vertex_list[k][v]
                self.gainbucket[k].append(vlink, vlink.data[0])
            vlink = self.gain_calc.vertex_list[pv][v]
            self.gainbucket[pv].set_key(vlink, 0)
            self.waitinglist.append(vlink)

        for v in self.hgr.module_fixed:
            self.lock_all(part[v], v)

        return totalcost

    def lock(self, whichPart, v):
        """
        The lock function sets a key by detaching a vertex link from a gain bucket and locking it.

        :param whichPart: An unsigned 8-bit integer representing a specific part or section
        :param v: The parameter `v` is of type `node_t`
        """
        vlink = self.gain_calc.vertex_list[whichPart][v]
        self.gainbucket[whichPart].detach(vlink)
        vlink.next = vlink  # lock

    def lock_all(self, _, v):
        """
        The `lock_all` function locks a specific vertex in a graph by detaching it from its bucket and
        setting its `next` attribute to itself.

        :param _: The underscore (_) is a convention in Python to indicate that a parameter is not going to
        be used in the function. It is often used as a placeholder when the function signature requires a
        certain number of parameters, but the function does not actually need to use all of them
        :param v: The parameter `v` represents the vertex that needs to be locked
        """
        for vlist, bckt in zip(self.gain_calc.vertex_list, self.gainbucket):
            vlink = vlist[v]
            bckt.detach(vlink)
            vlink.next = vlink  # lock

    def update_move_v(self, move_info_v, gain):
        """
        The function `update_move_v` updates the gain for a moving cell in a specific partition.

        :param move_info_v: A tuple containing three elements: v, from_part, and to_part
        :param gain: The `gain` parameter represents the gain value that needs to be updated for the moving
        cell
        """
        v, from_part, to_part = move_info_v
        for k in filter(lambda k: k != to_part, self.rr.exclude(from_part)):
            self.gainbucket[k].modify_key(
                self.gain_calc.vertex_list[k][v], self.gain_calc.delta_gain_v[k]
            )
        self._set_key(from_part, v, -gain)
        # self.lock(to_part, v)

    def modify_key(self, w, part_w, key):
        """
        The function `modify_key` modifies the key of a specific element in a dictionary.

        :param w: The parameter `w` is a variable of type that is not specified in the code snippet. It is
        used as an argument in the `modify_key` method
        :param part_w: The parameter `part_w` is not defined in the code snippet you provided. It seems to
        be missing or defined elsewhere in your code. Please provide more information or the definition of
        `part_w` so that I can assist you further
        :param key: The `key` parameter is a dictionary that contains keys and their corresponding values
        """
        for k in self.rr.exclude(part_w):
            self.gainbucket[k].modify_key(self.gain_calc.vertex_list[k][w], key[k])

    # private:

    def _set_key(self, whichPart, v, key):
        """
        The `_set_key` function sets a key value for a specific part and vertex in a gainbucket.

        :param whichPart: whichPart is a variable of type uint8_t. It is used to specify which part of the
        gainbucket to set the key for
        :param v: The parameter `v` is of type `node_t` and represents a node in the `vertex_list` of the
        `gain_calc` object
        :param key: The `key` parameter is an integer value that is used to set the key for a specific node
        in the `gainbucket` list
        """
        self.gainbucket[whichPart].set_key(
            self.gain_calc.vertex_list[whichPart][v], key
        )
