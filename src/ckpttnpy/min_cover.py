from typing import List, Set, Tuple

import networkx as nx

from .HierNetlist import HierNetlist
from .netlist import Netlist


def max_independent_net(H: Netlist, mw, DontSelect: Set) -> Tuple[Set, int]:
    """Maximum Independent NET (by greedy)

    Arguments:
        H (Netlist): [description]
        mw ([type]): [description]
        DontSelect (Set): [description]

    Returns:
        Tuple[Set, int]: [description]
    """
    visited = set()
    for net in DontSelect:
        visited.add(net)

    S = set()
    total_cost = 0

    for net in H.nets:
        if net in visited:
            continue
        if H.G.degree(net) < 2:
            continue
        S.add(net)
        total_cost += H.get_net_weight(net)
        for v in H.G[net]:
            for net2 in H.G[v]:
                visited.add(net2)
    return S, total_cost


def min_maximal_matching_pd(H: Netlist, matchset, weight, dep):
    """Perform minimum weighted maximal matching using primal-dual
    approximation algorithm

    Returns:
        [type]: [description]
    """
    def cover(net):
        for v in H.G[net]:
            dep[v] = True

    def any_of_dep(net):
        return any(dep[v] for v in H.G[net])

    gap = weight.copy()
    total_primal_cost = 0
    total_dual_cost = 0
    for net in H.nets:
        if any_of_dep(net):
            continue
        if matchset[net]:  # pre-define matching
            cover(net)
            continue
        min_val = gap[net]
        min_net = net
        for v in H.G[net]:
            for net2 in H.G[v]:
                if net2 == net or any_of_dep(net2):
                    continue
                if min_val > gap[net2]:
                    min_val = gap[net2]
                    min_net = net2
        cover(min_net)
        matchset[min_net] = True
        total_primal_cost += weight[min_net]
        total_dual_cost += min_val
        if min_net == net:
            continue
        gap[net] -= min_val
        for v in H[net]:
            for net2 in H.G[v]:
                if net2 == net:
                    continue
                gap[net2] -= min_val

    assert total_dual_cost <= total_primal_cost
    return total_primal_cost


# def min_net_cover_pd(H: Netlist, weight):
#     """Minimum Net Cover using Primal-Dual algorithm

#     @todo: sort cell weight to cover big cells first

#     Arguments:
#         H (type):  description
#         weight (type):  description

#     Returns:
#         dtype:  description
#     """
#     covered = set()
#     # S = set()
#     L = list()
#     if H.net_weight == {}:
#         gap = list(1 for _ in H.nets)
#     else:
#         gap = list(w for w in H.net_weight)
#     # gap = weight.copy()

#     total_primal_cost = 0
#     total_dual_cost = 0
#     # offset = H.number_of_modules()

#     for v in H.modules:
#         if v in covered:
#             continue
#         min_gap = 10000000
#         s = 0
#         for net in H.G[v]:
#             i_net = H.net_map[net]
#             if min_gap > gap[i_net]:
#                 s = net
#                 min_gap = gap[i_net]
#         # is_net_cover[i_s] = True
#         # S.append(i_s)
#         L.append(s)
#         for net in H.G[v]:
#             i_net = H.net_map[net]
#             gap[i_net] -= min_gap
#         assert gap[H.net_map[s]] == 0
#         for v2 in H.G[s]:
#             covered.add(v2)
#         total_primal_cost += H.get_net_weight(s)
#         total_dual_cost += min_gap

#     assert total_primal_cost >= total_dual_cost

#     # S2 = S.copy()
#     S = set(v for v in L)
#     for net in L:
#         found = False
#         for v in H.G[net]:
#             covered = False
#             for net2 in H.G[v]:
#                 if net2 == net:
#                     continue
#                 if net2 in S:
#                     covered = True
#                     break
#             if not covered:
#                 found = True
#                 break
#         if found:
#             continue
#         total_primal_cost -= H.get_net_weight(net)
#         S.remove(net)

#     return S, total_primal_cost


def create_contraction_subgraph(H: Netlist, DontSelect: Set) -> HierNetlist:
    S, _ = max_independent_net(H, H.module_weight, DontSelect)

    module_up_map: dict = {v: v for v in H.modules}
    # for v in H.modules:
    #     module_up_map[v] = v

    C: set = set()
    nets: List = []
    clusters: List = []
    cluster_map: dict = {}
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

    modules: List = [v for v in H.modules if v not in C]
    modules += clusters
    numModules = len(modules)
    numNets = len(nets)

    module_map = {v: i_v for i_v, v in enumerate(modules)}
    net_map = {net: i_net for i_net, net in enumerate(nets)}
    node_up_map = {v: module_map[module_up_map[v]] for v in H.modules}
    net_up_map = {net: net_map[net] + numModules for net in nets}
    # for net in nets:
    #     node_up_map[net] = net_map[net] + numModules
    node_up_map.update(net_up_map)

    G = nx.Graph()
    G.add_nodes_from(n for n in range(numModules + numNets))
    for v in H.modules:
        for net in H.G[v]:
            if net in S:
                continue
            G.add_edge(node_up_map[v], node_up_map[net])

    H2 = HierNetlist(G, range(numModules),
                     range(numModules, numModules + numNets))

    node_down_map = {v2: v1 for v1, v2 in node_up_map.items()}
    cluster_down_map = {node_up_map[v]: net for v, net in cluster_map.items()}

    module_weight = []
    for i_v in range(numModules):
        if i_v in cluster_down_map:
            net = cluster_down_map[i_v]
            cluster_weight = 0
            for v2 in H.G[net]:
                cluster_weight += H.get_module_weight(v2)
            module_weight.append(cluster_weight)
        else:
            v2 = node_down_map[i_v]
            module_weight.append(H.get_module_weight(v2))

    H2.node_up_map = node_up_map
    H2.node_down_map = node_down_map
    H2.cluster_down_map = cluster_down_map
    H2.module_weight = module_weight
    H2.parent = H
    return H2
