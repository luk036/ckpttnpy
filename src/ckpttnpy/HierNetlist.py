"""Hierarchical netlist for multi-level partitioning.

HierNetlist extends Netlist with cluster tracking, net weights,
and projection methods (up/down) for multi-level graph coarsening
and uncoarsening.
"""

from typing import Any, List, Union

import networkx as nx
from netlistx.netlist import Netlist


class HierNetlist(Netlist):
    """The `HierNetlist` class is a subclass of `Netlist` that represents a hierarchical netlist and
    includes additional attributes and methods for managing clusters and weights of nets.
    """

    parent: Netlist

    def __init__(self, ugraph: nx.Graph, modules: Any, nets: Any):
        Netlist.__init__(self, ugraph, modules, nets)

        self.node_down_list: List[Any] = []
        self.net_weight: dict = {}
        self.clusters: List[Any] = []

    def get_degree(self, v: Any) -> int:
        return sum(self.net_weight.get(net, 1) for net in self.ugraph[v])

    def get_max_degree(self) -> int:
        return max(self.get_degree(v) for v in self.modules)

    def projection_down(
        self, part: Union[dict, list], part_down: Union[dict, list]
    ) -> None:
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

    def projection_up(
        self, part: Union[dict, list], part_up: Union[dict, list]
    ) -> None:
        for v1, v2 in enumerate(self.node_down_list):
            part_up[v1] = part[v2]

    def get_net_weight(self, net: Any) -> int:
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
        weight = self.net_weight.get(net, 1)
        assert isinstance(weight, int), f"Expected int, got {type(weight)}"
        return weight
