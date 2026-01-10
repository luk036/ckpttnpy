"""
FMKWayGainMgr.py

This code defines a class called FMKWayGainMgr, which is designed to manage gains in a K-way
partitioned netlist. A netlist is a representation of connections between components in an
electronic circuit, and partitioning is the process of dividing these components into groups.
The purpose of this code is to help optimize the partitioning process by managing and calculating
gains, which represent the benefit of moving a component from one partition to another.

The FMKWayGainMgr class takes three inputs when initialized: a GainCalc object (which calculates gains),
a hypergraph (representing the netlist), and the number of partitions. It uses these inputs to set up
data structures for managing gains and partitions.

The main outputs of this class are not directly visible in the code, but it provides methods to
initialize, update, and manage gains for different components in the partitions. These gains can be
used by other parts of a larger system to make decisions about how to optimize the partitioning.

The class achieves its purpose through several key methods:

1. init: This method initializes or reinitializes the gain management system based on a given partition. It sets up gain buckets for each partition and calculates initial gains for each component.

2. lock and lock_all: These methods "lock" a component in a partition, preventing it from being moved. This is useful when certain components need to stay in place.

3. update_move_v: This method updates the gains when a component is moved from one partition to another.

4. modify_key: This method allows for modifying the gain values for a component across different partitions.

The logic flow in this code revolves around maintaining and updating gain values for components in
different partitions. It uses data structures like gainbuckets to efficiently manage these values.
The class also employs a round-robin approach (using the Robin class) to cycle through partitions
when performing operations.

An important aspect of the code is how it handles the gain calculations. While the actual
calculations are done by the GainCalc object, this class manages when and how these calculations
are applied, and how the results are stored and used.

Overall, this code provides a framework for managing the complex task of optimizing K-way partitions
in a netlist, which is a common problem in electronic design automation. It abstracts away many of
the details, providing a higher-level interface for working with partitions and their associated gains.
"""

from typing import Any, Dict, List, Union

from mywheel.robin import Robin  # for round-robin the partitions

from .FMGainMgr import FMGainMgr

Part = Union[Dict[Any, int], List[int]]


class FMKWayGainMgr(FMGainMgr):
    """
    The `FMBiGainMgr` class is a subclass of `FMGainMgr` (Fiduccia-Mattheyses Gain Manager) that provides methods for initialization and
    reinitialization of a K-way partitioned netlist.
    """

    def __init__(self, GainCalc, hyprgraph, num_parts: int):
        """
        The function initializes an object with the given parameters and calls the parent class's
        initialization method.

        :param GainCalc: The `GainCalc` parameter is a type or class that is used for calculating the gain
            of a netlist. It is likely a separate class that has methods or functions for calculating the gain
            based on certain criteria or algorithms
        :param hyprgraph: The `hyprgraph` parameter is of type `Netlist` and it represents a description of the netlist
        :param num_parts: The `num_parts` parameter is an integer that represents the number of partitions.
            It is of type `int`
        :type num_parts: int
        """
        FMGainMgr.__init__(self, GainCalc, hyprgraph, num_parts)
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

        for v in self.hyprgraph:
            pv = part[v]
            for k in self.rr.exclude(pv):
                vlink = self.gain_calc.vertex_list[k][v]
                self.gainbucket[k].append(vlink, vlink.data[0])
            vlink = self.gain_calc.vertex_list[pv][v]
            self.gainbucket[pv].set_key(vlink, 0)
            self.waitinglist.append(vlink)

        for v in self.hyprgraph.module_fixed:
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
        :param gain: The `gain` parameter represents the gain value that needs to be updated for the moving cell
        """
        v, from_part, to_part = move_info_v
        for k in [k for k in self.rr.exclude(from_part) if k != to_part]:
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

        Examples:
            >>> from ckpttnpy.FMKWayGainCalc import FMKWayGainCalc
            >>> from netlistx.netlist import Netlist
            >>> import networkx as nx
            >>> modules = ['a1', 'a2', 'a3', 'a4']
            >>> nets = ['n1', 'n2', 'n3']
            >>> G = nx.Graph()
            >>> G.add_nodes_from(modules, bipartite=0)
            >>> G.add_nodes_from(nets, bipartite=1)
            >>> G.add_edges_from([('a1', 'n1'), ('a1', 'n2'), ('a1', 'n3')])
            >>> hyprgraph = Netlist(G, modules, nets)
            >>> mgr = FMKWayGainMgr(FMKWayGainCalc, hyprgraph, 3)
            >>> part = {v: 0 for v in hyprgraph}
            >>> part['a1'] = 1
            >>> _ = mgr.init(part)
            >>> mgr.modify_key('a1', 1, {0: 2, 2: 3})
            >>> mgr.gainbucket[0].get_max()
            2
            >>> mgr.gainbucket[2].get_max()
            3
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
