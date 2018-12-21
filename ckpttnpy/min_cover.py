import networkx as nx
from .netlist import Netlist
import numpy as np

#
# Primal-dual algorithm for minimum vertex cover problem
#


def max_independent_net(H, weight):
    """Maximal Indepentent Net

    Arguments:
        H {[type]} -- [description]
        weight {[type]} -- [description]

    Returns:
        [type] -- [description]
    """
    visited = list(False for _ in H.nets)
    S = set()
    total_cost = 0
    for i_net, net in enumerate(H.nets):
        if visited[i_net]:
            continue
        S.add(net)
        total_cost += H.get_net_weight(net)
        for v in H.G[net]:
            for net2 in H.G[v]:
                i_net2 = H.net_map[net2]
                visited[i_net2] = True
    return S, total_cost


def min_net_cover_pd(H, weight):
    """Minimum Net Cover using Primal-Dual algorithm

    @todo: sort cell weight to cover big cells first

    Arguments:
        H {[type]} -- [description]
        weight {[type]} -- [description]

    Returns:
        [type] -- [description]
    """
    covered = set()
    # S = set()
    L = list()
    if H.net_weight == {}:
        gap = list(1 for _ in H.nets)
    else:
        gap = list(w for w in H.net_weight)
    # gap = weight.copy()

    total_primal_cost = 0
    total_dual_cost = 0
    # offset = H.number_of_modules()

    for v in H.modules:
        if v in covered:
            continue
        min_gap = 10000000
        s = 0
        for net in H.G[v]:
            i_net = H.net_map[net]
            if min_gap > gap[i_net]:
                s = net
                min_gap = gap[i_net]
        # is_net_cover[i_s] = True
        # S.append(i_s)
        L.append(s)
        for net in H.G[v]:
            i_net = H.net_map[net]
            gap[i_net] -= min_gap
        assert gap[H.net_map[s]] == 0
        for v2 in H.G[s]:
            covered.add(v2)
        total_primal_cost += H.get_net_weight(s)
        total_dual_cost += min_gap

    assert total_primal_cost >= total_dual_cost

    # S2 = S.copy()
    S = set(v for v in L)
    for net in L:
        found = False
        for v in H.G[net]:
            covered = False
            for net2 in H.G[v]:
                if net2 == net:
                    continue
                if net2 in S:
                    covered = True
                    break
            if not covered:
                found = True
                break
        if found:
            continue
        total_primal_cost -= H.get_net_weight(net)
        S.remove(net)

    return S, total_primal_cost


def create_contraction_subgraph(H):
    S, total_cost = max_independent_net(H, H.module_weight)

    module_up_map = {}
    for v in H.modules:
        module_up_map[v] = v

    C = set()
    nets = []
    clusters = []
    cluster_map = {}
    for net in H.nets:
        if net in S:
            netCur = iter(H.G[net])
            master = next(netCur)
            clusters.append(master)
            for v in H.G[net]:
                module_up_map[v] = master
                C.add(v)
            cluster_map[master] = net
        else:
            nets.append(net)

    modules = list(v for v in H.modules if v not in C)
    modules += clusters
    # nodes = modules + nets
    numModules = len(modules)
    numNets = len(nets)

    module_map = {}
    for i_v, v in enumerate(modules):
        module_map[v] = i_v

    net_map = {}
    for i_net, net in enumerate(nets):
        net_map[net] = i_net

    node_up_map = {}
    for v in H.modules:
        node_up_map[v] = module_map[module_up_map[v]]
    for net in H.nets:
        if net in S:
            continue
        node_up_map[net] = net_map[net] + numModules

    G = nx.Graph()
    G.add_nodes_from(list(n for n in range(numModules + numNets)))
    for v in H.modules:
        for net in H.G[v]:
            if net in S:
                continue
            G.add_edge(node_up_map[v], node_up_map[net])

    H2 = Netlist(G, range(numModules), range(numModules, numModules + numNets),
                 range(-numModules, numNets))
    H2.node_up_map = node_up_map

    node_down_map = {}
    for v1, v2 in node_up_map.items():
        node_down_map[v2] = v1
    H2.node_down_map = node_down_map

    cluster_down_map = {}
    for v, net in cluster_map.items():
        cluster_down_map[node_up_map[v]] = net
    H2.cluster_down_map = cluster_down_map

    module_weight = []
    for v in range(numModules):
        if v in cluster_down_map:
            net = cluster_down_map[v]
            cluster_weight = 0
            for v2 in H.G[net]:
                cluster_weight += H.get_module_weight(v2)
            module_weight.append(cluster_weight)
        else:
            v2 = node_down_map[v]
            module_weight.append(H.get_module_weight(v2))

    H2.module_weight = module_weight
    H2.parent = H
    return H2
