# from typing import Dict, List, Union
from collections.abc import Mapping

import networkx as nx

from .netlist import Netlist


class HierNetlist(Netlist):
    def __init__(self, gr: nx.Graph, modules, nets):
        """[summary]

        Arguments:
            gr (nx.Graph): [description]
            modules (Union[range, List]): [description]
            nets (Union[range, List]): [description]
        """
        Netlist.__init__(self, gr, modules, nets)
        self.parent = None
        # self.node_up_map: Mapping = {}
        self.node_down_list: Mapping = {}
        # self.cluster_down_map = None
        self.net_weight: dict = {}
        self.clusters = None
        self.num_clusters = 0

    def get_degree(self, v):
        return sum(self.net_weight.get(net, 1) for net in self.gr[v])

    def get_max_degree(self):
        return max(self.get_degree(v) for v in self.modules)

    def projection_down(self, part: Mapping, part_down: Mapping):
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
        # hgr = self.parent
        # for v in self.modules:
        #     if v in self.cluster_down_map:
        #         net = self.cluster_down_map[v]
        #         for v2 in hgr.gr[net]:
        #             part_down[v2] = part[v]
        #     else:
        #         v2 = self.node_down_list[v]
        #         part_down[v2] = part[v]
        #
        num_cells = self.num_modules - self.num_clusters
        for v1, v2 in enumerate(self.node_down_list):
            # TODO: take only first num_cells items
            part_down[v2] = part[v1]
        for i_v, net in enumerate(self.clusters):
            for v2 in self.parent.gr[net]:
                part_down[v2] = part[num_cells + i_v]

    def projection_up(self, part: Mapping, part_up: Mapping):
        """[summary]

        node_up_map:
            0 1 2 3 4 5 6 7 8 9,    parent
            3 3 4 2 0 2 3 4 3 1     self

        Args:
            part (Union[Dict, List[int]]): [description]
            part_up (Union[Dict, List[int]]): [description]
        """
        # for v in self.modules:
        #     part_up[v] = part[self.node_down_list[v]]
        for v1, v2 in enumerate(self.node_down_list):
            part_up[v1] = part[v2]
        # hgr = self.parent
        # for v in self.modules:
        #     if v in self.cluster_down_map:
        #         net = self.cluster_down_map[v]
        #         # for v2 in hgr.gr[net]:
        #         #     part_up[v] = part[v2]
        #         v2 = next(iter(hgr.gr[net]))  # pick the first one
        #         part_up[v] = part[v2]
        #     else:
        #         v2 = self.node_down_list[v]
        #         part_up[v] = part[v2]

        # for v in hgr:
        #     part_up[self.node_up_map[v]] = part[v]

    def get_net_weight(self, net) -> int:
        """[summary]

        Note: override the base class!

        Arguments:
            i_net (size_t):  description

        Returns:
            size_t:  description
        """
        return self.net_weight.get(net, 1)
