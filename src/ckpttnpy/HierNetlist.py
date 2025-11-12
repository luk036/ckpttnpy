"""
HierNetlist.py

This code defines a class called HierNetlist, which is designed to represent and manage a hierarchical netlist. A netlist is a description of how components in an electronic circuit are connected. The hierarchical aspect means it can handle nested or grouped components.

The HierNetlist class is built on top of a more basic Netlist class and adds functionality specific to hierarchical structures. It takes three main inputs when creating a new HierNetlist object: a graph representing the connections between components, a list of modules (which are the components), and a list of nets (which are the connections).

The class doesn't produce a specific output on its own, but it provides methods that can be used to manipulate and analyze the hierarchical netlist. These methods can be used by other parts of a program to perform various operations on the netlist.

The HierNetlist class achieves its purpose by storing additional information about the netlist structure. It keeps track of clusters (groups of components), weights of nets (importance or strength of connections), and a mapping between different levels of the hierarchy (node_down_list).

Some important functionalities provided by the class include:

1. Calculating the degree (number of connections) of a component, taking into account the weights of the connections.
2. Finding the maximum degree among all components in the netlist.
3. Projecting partitions (ways of dividing components) up and down the hierarchy. This allows for analyzing the netlist at different levels of detail.
4. Retrieving the weight of a specific net (connection).

The class uses data structures like lists and dictionaries to store and manage the hierarchical information. For example, the net_weight dictionary keeps track of the importance of each connection, while the clusters list stores information about grouped components.

Overall, this code provides a foundation for working with complex, hierarchical netlists in electronic design. It allows for operations that consider both the detailed connections between individual components and higher-level groupings of these components. This can be useful in tasks like circuit analysis, optimization, or layout planning in electronic design automation.
"""

from typing import Any, List

import networkx as nx
from netlistx.netlist import Netlist


class HierNetlist(Netlist):
    """The `HierNetlist` class is a subclass of `Netlist` that represents a hierarchical netlist and
    includes additional attributes and methods for managing clusters and weights of nets.
    """

    parent: Netlist

    def __init__(self, ugraph: nx.Graph, modules, nets):
        """
        The function initializes an object with a graph, modules, and nets, and sets some attributes.

        :param ugraph: ugraph is a variable of type nx.Graph, which represents a graph. It is used as an argument
            in the constructor of the class
        :type ugraph: nx.Graph
        :param modules: The `modules` parameter is either a range or a list that represents the modules in
            the graph. It contains the information about the modules present in the graph
        :param nets: The `nets` parameter is either a range or a list that represents the nets in the graph.
            A net is a collection of interconnected nodes in a circuit or network
        """
        Netlist.__init__(self, ugraph, modules, nets)

        self.node_down_list: List[Any] = []
        self.net_weight: dict = {}
        self.clusters: List[Any] = []

    def get_degree(self, v):
        """
        The function `get_degree` returns the sum of the weights of all edges connected to a given vertex.

        :param v: The parameter `v` represents a vertex in a graph
        :return: The function `get_degree` returns the sum of the values in the `net_weight` dictionary for
            each element in the `ugraph[v]` list.
        """
        return sum(self.net_weight.get(net, 1) for net in self.ugraph[v])

    def get_max_degree(self):
        """
        The function `get_max_degree` returns the maximum degree of all the modules in a graph.
        :return: the maximum degree of all the modules in the graph.
        """
        return max(self.get_degree(v) for v in self.modules)

    def projection_down(self, part, part_down):
        """
        The `projection_down` function assigns values from the `part` list to the `part_down` list based on
        the mapping defined by the `self.node_down_list` and `self.clusters` lists.

        .. svgbob::

            "self"       "parent"
          +--------+-----------------+
          | 3 3 3 2| 0 2 3 4 3 1     |
          | 0 1 2 3| 4 5 6 7 8 9,    |
          +--------+-----------------+

              "cluster_down_map"
            +-----+-----+-----+
            |  2  |  3  |  4  |
            +-----+-----+-----+
            | 10  | 13  | 12  |
            +-----+-----+-----+

        :param part: The `part` parameter is either a dictionary or a list of integers. It represents the
            partitioning of nodes in a graph
        :param part_down: The `part_down` parameter is either a dictionary or a list of integers. It
            represents the mapping of nodes in the `self.node_down_list` to their corresponding clusters in the
            `part` parameter
        """
        num_cells = len(self.node_down_list) - len(self.clusters)
        for v1, v2 in enumerate(self.node_down_list[:num_cells]):
            part_down[v2] = part[v1]
        for i_v, net in enumerate(self.clusters):
            p = part[num_cells + i_v]
            for v2 in self.parent.ugraph[net]:
                part_down[v2] = p

    def projection_up(self, part, part_up):
        """
        The `projection_up` function maps values from `part` to `part_up` based on the indices in
        `self.node_down_list`.

        :param part: The parameter `part` can be either a dictionary or a list of integers
        :param part_up: The `part_up` parameter is either a dictionary or a list of integers
        """
        for v1, v2 in enumerate(self.node_down_list):
            part_up[v1] = part[v2]

    def get_net_weight(self, net) -> int:
        """
        The function `get_net_weight` returns the net weight of a given net, with a default value of 1 if
        the net weight is not found.

        :param net: The parameter "net" in the get_net_weight method is the key used to retrieve the value
            from the net_weight dictionary
        :return: the value associated with the key 'net' in the dictionary 'self.net_weight'. If the key is
            not found in the dictionary, it will return 1.

        Examples:
            >>> import networkx as nx
            >>> G = nx.Graph()
            >>> modules = ['a1', 'a2', 'a3']
            >>> nets = ['n1', 'n2']
            >>> G.add_nodes_from(modules, bipartite=0)
            >>> G.add_nodes_from(nets, bipartite=1)
            >>> hgr = HierNetlist(G, modules, nets)
            >>> hgr.net_weight['n1'] = 2
            >>> hgr.get_net_weight('n1')
            2
            >>> hgr.get_net_weight('n2')
            1
        """
        return self.net_weight.get(net, 1)
