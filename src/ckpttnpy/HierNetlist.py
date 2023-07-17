import networkx as nx

from .netlist import Netlist

from typing import List, Any

# from typing import Mapping, MutableMapping


class HierNetlist(Netlist):
    parent: Netlist

    def __init__(self, gra: nx.Graph, modules, nets):
        """[summary]

        Arguments:
            gra (nx.Graph): [description]
            modules (Union[range, List]): [description]
            nets (Union[range, List]): [description]
        """
        Netlist.__init__(self, gra, modules, nets)
        # self.parent = self
        self.node_down_list: List[Any] = []
        self.net_weight: dict = {}
        self.clusters: List[Any] = []

    def get_degree(self, v):
        return sum(self.net_weight.get(net, 1) for net in self.gra[v])

    def get_max_degree(self):
        return max(self.get_degree(v) for v in self.modules)

    def projection_down(self, part, part_down):
        """[summary]

        3 3 3 2 0 2 3 4 3 1     self
        0 1 2 3 4 5 6 7 8 9,    parent

        cluster_down_map
        2   3   4
        10  13  12

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
        """[summary]

        Args:
            part (Union[Dict, List[int]]): [description]
            part_up (Union[Dict, List[int]]): [description]
        """
        for v1, v2 in enumerate(self.node_down_list):
            part_up[v1] = part[v2]

    def get_net_weight(self, net) -> int:
        """[summary]

        Note: override the base class!

        Arguments:
            i_net (size_t):  description

        Returns:
            size_t:  description
        """
        return self.net_weight.get(net, 1)
