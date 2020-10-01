# -*- coding: utf-8 -*-

import json
import random
from typing import Dict, List, Optional, Union

import networkx as nx
from networkx.algorithms import bipartite
from networkx.readwrite import json_graph


class ThinGraph(nx.Graph):
    all_edge_dict = {"weight": 1}

    def single_edge_dict(self):
        return self.all_edge_dict

    edge_attr_dict_factory = single_edge_dict
    node_attr_dict_factory = single_edge_dict


class SimpleGraph(nx.Graph):
    all_edge_dict = {"weight": 1}

    def single_edge_dict(self):
        return self.all_edge_dict

    edge_attr_dict_factory = single_edge_dict
    node_attr_dict_factory = single_edge_dict


class Netlist:
    num_pads = 0
    cost_model = 0

    def __init__(self, G: nx.Graph, modules: Union[range, List],
                 nets: Union[range, List]):
        """[summary]

        Arguments:
            G (nx.Graph): [description]
            modules (Union[range, List]): [description]
            nets (Union[range, List]): [description]
        """
        self.G = G
        self.modules = modules
        self.nets = nets

        self.num_modules = len(modules)
        self.num_nets = len(nets)
        self.net_weight: Optional[Union[Dict, List[int]]] = None
        self.module_weight: Optional[Union[Dict, List[int]]] = None
        self.module_fixed: set = set()

        # for hierachical netlist and multilevel algorithm
        self.parent = self
        self.node_up_map: dict = {}
        self.node_down_map: dict = {}
        self.cluster_down_map: dict = {}

        # self.module_dict = {}
        # for v in enumerate(self.module_list):
        #     self.module_dict[v] = v

        # self.net_dict = {}
        # for i_net, net in enumerate(self.net_list):
        #     self.net_dict[net] = i_net

        # self.module_fixed = module_fixed
        # self.has_fixed_modules = (self.module_fixed != [])
        self.max_degree = max(self.G.degree[cell] for cell in modules)
        self.max_net_degree = max(self.G.degree[net] for net in nets)

    def number_of_modules(self) -> int:
        """[summary]

        Returns:
            dtype:  description
        """
        return self.num_modules

    def number_of_nets(self) -> int:
        """[summary]

        Returns:
            dtype:  description
        """
        return self.num_nets

    def number_of_nodes(self) -> int:
        """[summary]

        Returns:
            dtype:  description
        """
        return self.G.number_of_nodes()

    def number_of_pins(self) -> int:
        """[summary]

        Returns:
            dtype:  description
        """
        return self.G.number_of_edges()

    def get_max_degree(self) -> int:
        """[summary]

        Returns:
            dtype:  description
        """
        return self.max_degree

    def get_max_net_degree(self) -> int:
        """[summary]

        Returns:
            dtype:  description
        """
        return self.max_net_degree

    def get_module_weight(self, v) -> int:
        """[summary]

        Arguments:
            v (size_t):  description

        Returns:
            [size_t]:  description
        """
        return 1 if self.module_weight is None \
            else self.module_weight[v]

    # def get_module_weight_by_id(self, v):
    #     """[summary]

    #     Arguments:
    #         v (size_t):  description

    #     Returns:
    #         [size_t]:  description
    #     """
    #     return 1 if self.module_weight is None \
    #         else self.module_weight[v]

    def get_net_weight(self, net) -> int:
        """[summary]

        Arguments:
            i_net (size_t):  description

        Returns:
            size_t:  description
        """
        # return 1 if self.net_weight == [] \
        #          else self.net_weight[self.net_map[net]]
        return 1

    # def project_down(self, part, part_down):
    #     H = self.parent
    #     for i_v, v in enumerate(self.modules):
    #         if v in self.cluster_down_map:
    #             net = self.cluster_down_map[v]
    #             for v2 in H.G[net]:
    #                 i_v2 = H.module_map[v2]
    #                 part_down[v2] = part[v]
    #         else:
    #             v2 = self.node_down_map[v]
    #             i_v2 = H.module_map[v2]
    #             part_down[v2] = part[v]

    # def project_up(self, part, part_up):
    #     H = self.parent
    #     for i_v, v in enumerate(H.modules):
    #         part_up[self.node_up_map[v]] = part[v]

    def projection_down(self, part: Union[Dict, List[int]],
                        part_down: Union[Dict, List[int]]):
        H = self.parent

        for v in self.modules:
            if v in self.cluster_down_map:
                net = self.cluster_down_map[v]
                for v2 in H.G[net]:
                    part_down[v2] = part[v]
            else:
                v2 = self.node_down_map[v]
                part_down[v2] = part[v]

    def projection_up(self, part: Union[Dict, List[int]],
                      part_up: Union[Dict, List[int]]):
        H = self.parent

        for v in H.modules:
            part_up[self.node_up_map[v]] = part[v]

        # if not extern_nets:
        #     return

        # extern_nets_up.clear()
        # for net in extern_nets:
        #     extern_nets_up.add(self.node_up_map[net])

        # K = len(extern_modules)
        # extern_modules_up = list(set() for _ in K)

        # for k in range(K):
        #     for v in extern_modules[k]:
        #         v2 = self.node_up_map[v]
        #         extern_modules_up[k].add(v2)


def read_json(filename):
    with open(filename, 'r') as fr:
        data = json.load(fr)
    G = json_graph.node_link_graph(data)
    num_modules = G.graph['num_modules']
    num_nets = G.graph['num_nets']
    num_pads = G.graph['num_pads']
    H = Netlist(G, range(num_modules),
                range(num_modules, num_modules + num_nets))
    H.num_pads = num_pads
    return H


def create_drawf():
    G = ThinGraph()
    G.add_nodes_from([
        'a0',
        'a1',
        'a2',
        'a3',
        'p1',
        'p2',
        'p3',
        'n0',
        'n1',
        'n2',
        'n3',
        'n4',
        'n5',
    ])
    nets = [
        'n0',
        'n1',
        'n2',
        'n3',
        'n4',
        'n5',
    ]
    # net_map = {net: i_net for i_net, net in enumerate(nets)}
    modules = ['a0', 'a1', 'a2', 'a3', 'p1', 'p2', 'p3']
    # module_map = {v: i_v for i_v, v in enumerate(modules)}
    # module_weight = [1, 3, 4, 2, 0, 0, 0]
    module_weight = {
        'a0': 1,
        'a1': 3,
        'a2': 4,
        'a3': 2,
        'p1': 0,
        'p2': 0,
        'p3': 0
    }

    G.add_edges_from([('n0', 'p1', {
        'dir': 'I'
    }), ('n0', 'a0', {
        'dir': 'I'
    }), ('n0', 'a1', {
        'dir': 'O'
    }), ('n1', 'a0', {
        'dir': 'I'
    }), ('n1', 'a2', {
        'dir': 'I'
    }), ('n1', 'a3', {
        'dir': 'O'
    }), ('n2', 'a1', {
        'dir': 'I'
    }), ('n2', 'a2', {
        'dir': 'I'
    }), ('n2', 'a3', {
        'dir': 'O'
    }), ('n3', 'a2', {
        'dir': 'I'
    }), ('n3', 'p2', {
        'dir': 'O'
    }), ('n4', 'a3', {
        'dir': 'I'
    }), ('n4', 'p3', {
        'dir': 'O'
    }), ('n5', 'p2', {
        'dir': 'B'
    })])
    G.graph['num_modules'] = 7
    G.graph['num_nets'] = 6
    G.graph['num_pads'] = 3
    H = Netlist(G, modules, nets)
    H.module_weight = module_weight
    H.num_pads = 3
    return H


def create_test_netlist():
    G = ThinGraph()
    G.add_nodes_from(['a0', 'a1', 'a2', 'a3', 'a4', 'a5'])
    # module_weight = [533, 543, 532]
    module_weight = {'a0': 533, 'a1': 543, 'a2': 532}
    G.add_edges_from([
        ('a3', 'a0'),
        ('a3', 'a1'),
        ('a4', 'a0'),
        ('a4', 'a1'),
        ('a4', 'a2'),
        ('a5', 'a0')  # self-loop
    ])

    G.graph['num_modules'] = 3
    G.graph['num_nets'] = 3
    modules = ['a0', 'a1', 'a2']
    # module_map = {v: i_v for i_v, v in enumerate(modules)}
    nets = ['a3', 'a4', 'a5']
    # net_map = {net: i_net for i_net, net in enumerate(nets)}

    H = Netlist(G, modules, nets)
    H.module_weight = module_weight
    return H


def vdc(n, base=2):
    """[summary]

    Arguments:
        n ([type]): [description]

    Keyword Arguments:
        base (int): [description] (default: {2})

    Returns:
        [type]: [description]
    """
    vdc, denom = 0., 1.
    while n:
        denom *= base
        n, remainder = divmod(n, base)
        vdc += remainder / denom
    return vdc


def vdcorput(n, base=2):
    """[summary]

    Arguments:
        n (int): number of vectors

    Keyword Arguments:
        base (int): [description] (default: {2})

    Returns:
        [type]: [description]
    """
    return [vdc(i, base) for i in range(n)]


def formGraph(N, M, pos, eta, seed=None):
    """Form N by N grid of nodes, connect nodes within eta.
        mu and eta are relative to 1/(N-1)

    Arguments:
        t (float): the best-so-far optimal value
        pos ([type]): [description]
        eta ([type]): [description]

    Keyword Arguments:
        seed ([type]): [description] (default: {None})

    Returns:
        [type]: [description]
    """
    if seed:
        random.seed(seed)

    # connect nodes with edges
    G = bipartite.random_graph(N, M, eta)
    # G = nx.DiGraph(G)
    return G


def create_random_graph(N=30, M=26, eta=0.1):
    T = N + M
    xbase = 2
    ybase = 3
    x = [i for i in vdcorput(T, xbase)]
    y = [i for i in vdcorput(T, ybase)]
    pos = zip(x, y)
    G = formGraph(N, M, pos, eta, seed=5)

    G.graph['num_modules'] = N
    G.graph['num_nets'] = M
    H = Netlist(G, range(N), range(N, N + M))
    return H
