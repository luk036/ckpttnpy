# -*- coding: utf-8 -*-

from typing import Dict, List, Union

import networkx as nx

from .netlist import Netlist


class HierNetlist(Netlist):
    def __init__(self, G: nx.Graph, modules, nets):
        """[summary]

        Arguments:
            G (nx.Graph): [description]
            modules (Union[range, List]): [description]
            nets (Union[range, List]): [description]
        """
        Netlist.__init__(self, G, modules, nets)
        self.parent = None
        self.node_up_map: Union[Dict, List] = {}
        self.node_down_map: Union[Dict, List] = {}
        self.cluster_down_map: dict = {}
        self.net_weight: dict = {}

    def get_degree(self, v):
        return sum(self.net_weight.get(net, 1) for net in self.G[v])

    def get_max_degree(self):
        return max(self.get_degree(v) for v in self.modules)

    def projection_down(
        self, part: Union[Dict, List[int]], part_down: Union[Dict, List[int]]
    ):
        """[summary]

        Args:
            part (Union[Dict, List[int]]): [description]
            part_down (Union[Dict, List[int]]): [description]
        """
        H = self.parent
        for v in self.modules:
            if v in self.cluster_down_map:
                net = self.cluster_down_map[v]
                for v2 in H.G[net]:
                    part_down[v2] = part[v]
            else:
                v2 = self.node_down_map[v]
                part_down[v2] = part[v]

    def projection_up(
        self, part: Union[Dict, List[int]], part_up: Union[Dict, List[int]]
    ):
        """[summary]

        Args:
            part (Union[Dict, List[int]]): [description]
            part_up (Union[Dict, List[int]]): [description]
        """
        H = self.parent
        for v in H:
            part_up[self.node_up_map[v]] = part[v]

    def get_net_weight(self, net) -> int:
        """[summary]

        Arguments:
            i_net (size_t):  description

        Returns:
            size_t:  description
        """
        return self.net_weight.get(net, 1)
