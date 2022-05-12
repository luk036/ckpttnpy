from typing import List, Set

import networkx as nx

from .HierNetlist import HierNetlist
from .netlist import Netlist

# from .minhash import MinHash


def min_maximal_matching(hgr, weight, matchset, dep):
    """Perform minimum weighted maximal matching using primal-dual
    approximation algorithm

    Returns:
        [type]: [description]
    """

    def cover(net):
        for v in hgr.gr[net]:
            dep.add(v)

    def any_of_dep(net):
        return any(v in dep for v in hgr.gr[net])

    gap = weight.copy()
    total_primal_cost = 0
    total_dual_cost = 0
    for net in filter(
        lambda net: any_of_dep(net) is False and (net in matchset) is False, hgr.nets
    ):
        min_val = gap[net]
        min_net = net
        for v in hgr.gr[net]:
            for net2 in filter(lambda net2: any_of_dep(net2) is False, hgr.gr[v]):
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
        for v in hgr.gr[net]:
            for net2 in hgr.gr[v]:
                # if net2 == net:
                #     continue
                gap[net2] -= min_val

    assert total_dual_cost <= total_primal_cost
    return total_primal_cost


def create_contraction_subgraph(
    hgr: Netlist, module_weight, DontSelect: Set
) -> HierNetlist:
    """[summary]

    Args:
        hgr (Netlist): [description]
        DontSelect (Set): [description]

    Returns:
        HierNetlist: [description]
    """
    # s1, _ = max_independent_net(hgr, hgr.module_weight, DontSelect)
    # weight = dict()
    # for net in hgr.nets:
    #     weight[net] = sum(hgr.get_module_weight(v) for v in hgr.gr[net])
    weight = {
        net: sum(module_weight[v] for v in hgr.gr[net]) for net in hgr.nets
    }  # can be done in parallel
    s1 = set()
    _ = min_maximal_matching(hgr, weight, s1, DontSelect)

    module_up_map: dict = {v: v for v in hgr}
    # for v in hgr:
    #     module_up_map[v] = v

    C = set()
    nets = list()
    clusters = list()
    # cluster_map = dict()
    for net in hgr.nets:
        if net in s1:
            # net_cur = iter(hgr.gr[net])
            # master = next(net_cur)
            # clusters.append(master)
            clusters.append(net)
            module_up_map.update({v: net for v in hgr.gr[net]})
            C.update(v for v in hgr.gr[net])
            # cluster_map[master] = net
        else:
            nets.append(net)

    modules: List = [v for v in hgr if v not in C]

    # no more C
    C.clear()

    modules += clusters
    numModules = len(modules)
    numNets = len(nets)

    module_map = {v: i_v for i_v, v in enumerate(modules)}
    # net_map = {net: i_net for i_net, net in enumerate(nets)}
    node_up_dict = {v: module_map[module_up_map[v]] for v in hgr}
    net_up_map = {net: i_net + numModules for i_net, net in enumerate(nets)}
    # for net in nets:
    #     node_up_map[net] = net_map[net] + numModules
    # node_up_dict.update(net_up_map)

    gr = nx.Graph()
    gr.add_nodes_from(n for n in range(numModules + numNets))
    for v in hgr:
        for net in filter(lambda net: net not in s1, hgr.gr[v]):
            gr.add_edge(node_up_dict[v], net_up_map[net])
            # automatically merge the same cell-net

    # Purging duplicate nets
    net_weight = dict()
    for net in nets:
        wt = hgr.get_net_weight(net)
        if wt > 1:
            net_weight[net_up_map[net]] = wt

    removelist = set()
    for net in clusters:
        cluster = module_map[net]
        for net1 in gr[cluster]:
            if gr.degree(net1) == 1:  # self loop
                removelist.add(net1)
                continue
            for net2 in filter(
                lambda net2: net2 != net1 and gr.degree(net2) == gr.degree(net1),
                gr[cluster],
            ):
                same = False
                if gr.degree(net1) <= 3:  # only check for low-fan-out nets
                    set1 = set(v for v in gr[net1])
                    set2 = set(v for v in gr[net2])
                    if set1 == set2:
                        same = True
                # else:
                #     m1 = MinHash(100)
                #     m2 = MinHash(100)
                #     for v1 in gr[net1]:
                #         m1.add(v1)
                #     for v2 in gr[net2]:
                #         m2.add(v2)
                #     if m1.jaccard(m2) > 0.99:
                #         same = True
                if same:
                    removelist.add(net2)
                    net_weight[net1] = net_weight.get(net1, 1) + net_weight.get(net2, 1)
    gr.remove_nodes_from(removelist)
    original_net = range(numModules, numModules + numNets)
    updated_nets = [net for net in original_net if net not in removelist]

    hgr2 = HierNetlist(gr, range(numModules), updated_nets)

    # node_down_map = {v2: v1 for v1, v2 in node_up_map.items()}
    node_down_map = [0] * numModules
    for v1, v2 in node_up_dict.items():
        node_down_map[v2] = v1

    # cluster_down_map = {node_up_dict[v]: net
    #     for v, net in cluster_map.items()}
    cluster_down_map = {node_up_dict[v]: netk for netk in s1 for v in hgr.gr[netk]}

    module_weight2 = [0] * numModules
    for i_v in range(numModules):
        if i_v in cluster_down_map:
            net = cluster_down_map[i_v]
            # cluster_weight = 0
            # for v2 in hgr.gr[net]:
            #     cluster_weight += hgr.get_module_weight(v2)
            # cluster_weight = sum(hgr.get_module_weight(v) for v in hgr.gr[net])
            cluster_weight = weight[net]
            module_weight2[i_v] = cluster_weight
        else:
            v2 = node_down_map[i_v]
            module_weight2[i_v] = module_weight[v2]

    if isinstance(hgr.modules, range):
        node_up_map = [0 for _ in hgr.modules]
    elif isinstance(hgr.modules, list):
        node_up_map = {}
    else:
        raise NotImplementedError

    for v in hgr.modules:
        node_up_map[v] = node_up_dict[v]

    hgr2.node_up_map = node_up_map
    hgr2.node_down_map = node_down_map
    hgr2.cluster_down_map = cluster_down_map
    hgr2.module_weight = module_weight2
    hgr2.net_weight = net_weight
    # hgr2.net_weight = shift_array(1 for _ in range(numNets))
    # hgr2.net_weight.set_start(numModules)
    hgr2.parent = hgr
    return hgr2, module_weight2
