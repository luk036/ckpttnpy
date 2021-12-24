from typing import List, Set

import networkx as nx

from .HierNetlist import HierNetlist
from .netlist import Netlist

# from .minhash import MinHash


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
    for net in filter(
        lambda net: any_of_dep(net) is False and (net in matchset) is False, H.nets
    ):
        min_val = gap[net]
        min_net = net
        for v in H.G[net]:
            for net2 in filter(lambda net2: any_of_dep(net2) is False, H.G[v]):
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


def create_contraction_subgraph(
    H: Netlist, module_weight, DontSelect: Set
) -> HierNetlist:
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
        net: sum(module_weight[v] for v in H.G[net]) for net in H.nets
    }  # can be done in parallel
    S = set()
    _ = min_maximal_matching(H, weight, S, DontSelect)

    module_up_map: dict = {v: v for v in H}
    # for v in H:
    #     module_up_map[v] = v

    C = set()
    nets = list()
    clusters = list()
    # cluster_map = dict()
    for net in H.nets:
        if net in S:
            # netCur = iter(H.G[net])
            # master = next(netCur)
            # clusters.append(master)
            clusters.append(net)
            module_up_map.update({v: net for v in H.G[net]})
            C.update(v for v in H.G[net])
            # cluster_map[master] = net
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

    # Purging duplicate nets
    net_weight = dict()
    for net in nets:
        wt = H.get_net_weight(net)
        if wt > 1:
            net_weight[net_up_map[net]] = wt

    removelist = set()
    for net in clusters:
        cluster = module_map[net]
        for net1 in G[cluster]:
            if G.degree(net1) == 1:  # self loop
                removelist.add(net1)
                continue
            for net2 in filter(
                lambda net2: net2 != net1 and G.degree(net2) == G.degree(net1),
                G[cluster],
            ):
                same = False
                if G.degree(net1) <= 3:  # only check for low-fan-out nets
                    S1 = set(v for v in G[net1])
                    S2 = set(v for v in G[net2])
                    if S1 == S2:
                        same = True
                # else:
                #     m1 = MinHash(100)
                #     m2 = MinHash(100)
                #     for v1 in G[net1]:
                #         m1.add(v1)
                #     for v2 in G[net2]:
                #         m2.add(v2)
                #     if m1.jaccard(m2) > 0.99:
                #         same = True
                if same:
                    removelist.add(net2)
                    net_weight[net1] = net_weight.get(net1, 1) + net_weight.get(net2, 1)
    G.remove_nodes_from(removelist)
    original_net = range(numModules, numModules + numNets)
    updated_nets = [net for net in original_net if net not in removelist]

    H2 = HierNetlist(G, range(numModules), updated_nets)

    # node_down_map = {v2: v1 for v1, v2 in node_up_map.items()}
    node_down_map = [0 for _ in range(numModules)]
    for v1, v2 in node_up_dict.items():
        node_down_map[v2] = v1

    # cluster_down_map = {node_up_dict[v]: net
    #     for v, net in cluster_map.items()}
    cluster_down_map = {node_up_dict[v]: netk for netk in S for v in H.G[netk]}

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
    H2.net_weight = net_weight
    # H2.net_weight = shift_array(1 for _ in range(numNets))
    # H2.net_weight.set_start(numModules)
    H2.parent = H
    return H2, module_weight2
