from typing import List, Set

import networkx as nx

from .array_like import repeat_array
from .HierNetlist import HierNetlist
from .netlist import Netlist

# def max_independent_net(H: Netlist, mw, DontSelect: Set) -> Tuple[Set, int]:
#     """Maximum Independent NET (by greedy)

#     Arguments:
#         H (Netlist): [description]
#         mw ([type]): [description]
#         DontSelect (Set): [description]

#     Returns:
#         Tuple[Set, int]: [description]
#     """
#     visited = set()
#     for net in DontSelect:
#         visited.add(net)

#     S = set()
#     total_cost = 0

#     for net in H.nets:
#         if net in visited:
#             continue
#         if H.G.degree(net) < 2:
#             continue
#         S.add(net)
#         total_cost += H.get_net_weight(net)
#         for v in H.G[net]:
#             for net2 in H.G[v]:
#                 visited.add(net2)
#     return S, total_cost


def min_maximal_matching(H, weight, matchset, dep):
    """Perform minimum weighted maximal matching using primal-dual
    approximation algorithm

    Returns:
        [type]: [description]
    """
    def cover(net):
        for v in H.G[net]:
            dep.add(v)

    def any_of_dep(net):
        return any(v in dep for v in H.G[net])

    gap = weight.copy()
    total_primal_cost = 0
    total_dual_cost = 0
    for net in H.nets:
        if any_of_dep(net):
            continue
        if net in matchset:  # pre-define matching
            # cover(net)
            continue
        min_val = gap[net]
        min_net = net
        for v in H.G[net]:
            for net2 in H.G[v]:
                if any_of_dep(net2):
                    continue
                if min_val > gap[net2]:
                    min_val = gap[net2]
                    min_net = net2
        cover(min_net)
        matchset.add(min_net)
        total_primal_cost += weight[min_net]
        total_dual_cost += min_val
        if min_net == net:
            continue
        gap[net] -= min_val
        for v in H.G[net]:
            for net2 in H.G[v]:
                # if net2 == net:
                #     continue
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

#     for v in H:
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


def create_contraction_subgraph(H: Netlist, module_weight,
                                DontSelect: Set) -> HierNetlist:
    """[summary]

    Args:
        H (Netlist): [description]
        DontSelect (Set): [description]

    Returns:
        HierNetlist: [description]
    """
    # S, _ = max_independent_net(H, H.module_weight, DontSelect)
    # weight = dict()
    # for net in H.nets:
    #     weight[net] = sum(H.get_module_weight(v) for v in H.G[net])
    weight = {
        net: sum(module_weight[v] for v in H.G[net])
        for net in H.nets
    }
    S = set()
    _ = min_maximal_matching(H, weight, S, DontSelect)

    module_up_map: dict = {v: v for v in H}
    # for v in H:
    #     module_up_map[v] = v

    C = set()
    nets = list()
    clusters = list()
    cluster_map = dict()
    for net in H.nets:
        if net in S:
            netCur = iter(H.G[net])
            master = next(netCur)
            clusters.append(master)
            module_up_map.update({v: master for v in H.G[net]})
            C.update(v for v in H.G[net])
            cluster_map[master] = net
        else:
            nets.append(net)

    modules: List = [v for v in H if v not in C]

    # no more C
    C.clear()

    modules += clusters
    numModules = len(modules)
    numNets = len(nets)

    module_map = {v: i_v for i_v, v in enumerate(modules)}
    # net_map = {net: i_net for i_net, net in enumerate(nets)}
    node_up_dict = {v: module_map[module_up_map[v]] for v in H}
    net_up_map = {net: i_net + numModules for i_net, net in enumerate(nets)}
    # for net in nets:
    #     node_up_map[net] = net_map[net] + numModules
    # node_up_dict.update(net_up_map)

    G = nx.Graph()
    G.add_nodes_from(n for n in range(numModules + numNets))
    for v in H:
        for net in filter(lambda net: net not in S, H.G[v]):
            G.add_edge(node_up_dict[v], net_up_map[net])
            # automatically merge the same cell-net

    H2 = HierNetlist(G, range(numModules),
                     range(numModules, numModules + numNets))

    # node_down_map = {v2: v1 for v1, v2 in node_up_map.items()}
    node_down_map = [0 for _ in range(numModules)]
    for v1, v2 in node_up_dict.items():
        node_down_map[v2] = v1

    cluster_down_map = {node_up_dict[v]: net for v, net in cluster_map.items()}

    module_weight2 = list(0 for _ in range(numModules))
    for i_v in range(numModules):
        if i_v in cluster_down_map:
            net = cluster_down_map[i_v]
            # cluster_weight = 0
            # for v2 in H.G[net]:
            #     cluster_weight += H.get_module_weight(v2)
            # cluster_weight = sum(H.get_module_weight(v) for v in H.G[net])
            cluster_weight = weight[net]
            module_weight2[i_v] = cluster_weight
        else:
            v2 = node_down_map[i_v]
            module_weight2[i_v] = module_weight[v2]

    if isinstance(H.modules, range):
        node_up_map = [0 for _ in H.modules]
    elif isinstance(H.modules, list):
        node_up_map = {}
    else:
        raise NotImplementedError

    for v in H.modules:
        node_up_map[v] = node_up_dict[v]

    H2.node_up_map = node_up_map
    H2.node_down_map = node_down_map
    H2.cluster_down_map = cluster_down_map
    H2.module_weight = module_weight2
    H2.net_weight = repeat_array(1, numNets)
    # H2.net_weight = shift_array(1 for _ in range(numNets))
    # H2.net_weight.set_start(numModules)
    H2.parent = H
    return H2, module_weight2
