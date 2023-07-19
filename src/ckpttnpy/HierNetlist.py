import networkx as nx

from .netlist import Netlist

from typing import List, Any

# from typing import Mapping, MutableMapping


class HierNetlist(Netlist):
    """The `HierNetlist` class is a subclass of `Netlist` that represents a hierarchical netlist and
    includes additional attributes and methods for managing clusters and weights of nets.
    """

    parent: Netlist

    def __init__(self, gra: nx.Graph, modules, nets):
        """
        The function initializes an object with a graph, modules, and nets, and sets some attributes.

        :param gra: gra is a variable of type nx.Graph, which represents a graph. It is used as an argument
        in the constructor of the class
        :type gra: nx.Graph
        :param modules: The `modules` parameter is either a range or a list that represents the modules in
        the graph. It contains the information about the modules present in the graph
        :param nets: The `nets` parameter is either a range or a list that represents the nets in the graph.
        A net is a collection of interconnected nodes in a circuit or network
        """
        Netlist.__init__(self, gra, modules, nets)
        # self.parent = self
        self.node_down_list: List[Any] = []
        self.net_weight: dict = {}
        self.clusters: List[Any] = []

    def get_degree(self, v):
        """
        The function `get_degree` returns the sum of the weights of all edges connected to a given vertex.

        :param v: The parameter `v` represents a vertex in a graph
        :return: The function `get_degree` returns the sum of the values in the `net_weight` dictionary for
        each element in the `gra[v]` list.
        """
        return sum(self.net_weight.get(net, 1) for net in self.gra[v])

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

        3 3 3 2 0 2 3 4 3 1     self
        0 1 2 3 4 5 6 7 8 9,    parent

        cluster_down_map
        2   3   4
        10  13  12

        :param part: The `part` parameter is either a dictionary or a list of integers. It represents the
        partitioning of nodes in a graph
        :param part_down: The `part_down` parameter is either a dictionary or a list of integers. It
        represents the mapping of nodes in the `self.node_down_list` to their corresponding clusters in the
        `part` parameter

        Args:
            part (Union[Dict, List[int]]): [description]
            part_down (Union[Dict, List[int]]): [description]
        """
        num_cells = len(self.node_down_list) - len(self.clusters)
        for v1, v2 in enumerate(self.node_down_list[:num_cells]):
            part_down[v2] = part[v1]
        for i_v, net in enumerate(self.clusters):
            p = part[num_cells + i_v]
            for v2 in self.parent.gra[net]:
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
        """
        return self.net_weight.get(net, 1)
