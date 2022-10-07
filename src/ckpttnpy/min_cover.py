from typing import Set

# import networkx as nx

from .HierNetlist import HierNetlist
from .netlist import Netlist, TinyGraph
from .array_like import shift_array
# from .minhash import MinHash

"""
Notes:
    module and net should have a unique id because
    they tread the same node in the underlying graph.
"""


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
    for net in filter(lambda net: not (any_of_dep(net)
                      or (net in matchset)), hgr.nets):
        min_val = gap[net]
        min_net = net
        for v in hgr.gr[net]:
            for net2 in filter(lambda net2: not
                               any_of_dep(net2), hgr.gr[v]):
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


def contract_subgraph(hgr: Netlist, module_weight, forbid: Set) -> HierNetlist:
    """[summary]

    Args:
        hgr (Netlist): [description]
        forbid (Set): [description]

    Returns:
        HierNetlist: [description]
    """
    cluster_weight = {
        net: sum(module_weight[v] for v in hgr.gr[net]) for net in hgr.nets
    }  # can be done in parallel
    s1 = set()  # initially no preferrence
    min_maximal_matching(hgr, cluster_weight, s1, forbid)

    module_up_map: dict = {v: v for v in hgr}  # initially map to itself

    covered = set()
    nets = list()
    clusters = list()
    # cluster_map = dict()
    for net in hgr.nets:
        if net in s1:
            clusters.append(net)
            module_up_map.update({v: net for v in hgr.gr[net]})
            covered.update(v for v in hgr.gr[net])
        else:
            nets.append(net)
    s1.clear()  # no more s1

    modules = [v for v in hgr if v not in covered]
    modules += clusters
    num_modules = len(modules)
    num_clusters = len(clusters)

    covered.clear()  # no more covered

    module_map = {v: i_v for i_v, v in enumerate(modules)}
    # net_map = {net: i_net for i_net, net in enumerate(nets)}
    node_up_dict = {v: module_map[module_up_map[v]] for v in hgr}
    module_up_map.clear()  # no more module_up_map
    module_map.clear()  # no more module_map
    # net_up_map = {net: i_net + num_modules for i_net, net in enumerate(nets)}

    gr = TinyGraph()  # gr is a bipartite graph
    gr.init_nodes(num_modules + len(nets))
    # gr = nx.Graph()
    # gr.add_nodes_from(n for n in range(num_modules + len(nets)))

    # for v in hgr:
    #     for net in filter(lambda net: net not in s1, hgr.gr[v]):
    #         gr.add_edge(node_up_dict[v], net_up_map[net])
    #         # automatically merge the same cell-net
    # for net in nets:
    #     for v in hgr.gr[net]:
    #         gr.add_edge(node_up_dict[v], net_up_map[net])
    for i_net, net in enumerate(nets):
        for v in hgr.gr[net]:
            gr.add_edge(node_up_dict[v], i_net + num_modules)

    # Purging duplicate nets
    net_weight, removelist = purge_duplicate_nets(
        hgr, gr, nets, num_clusters, num_modules)
    # net_up_map.clear()  # no more net_up_map

    # Reconstruct a new graph with purged nets
    original_net = range(num_modules, num_modules + len(nets))
    updated_nets = [net for net in original_net if net not in removelist]
    # nets_enum = enumerate(net for net in original_net
    #                       if net not in removelist)
    net_up_map2 = {net: i_net + num_modules
                   for i_net, net in enumerate(updated_nets)}
    num_nets = len(nets) - len(removelist)
    gr2 = TinyGraph()
    gr2.init_nodes(num_modules + num_nets)
    # gr2 = nx.Graph()
    # gr2.add_nodes_from(n for n in range(num_modules + num_nets))

    # for v in range(num_modules):
    #     for net in filter(lambda net1: net1 not in removelist, gr[v]):
    #         assert net >= num_modules
    #         assert net < num_modules + len(nets)
    #         gr2.add_edge(v, net_up_map2[net])

    for i_net, net in enumerate(updated_nets):
        for v in gr[net]:
            assert net >= num_modules
            assert net < num_modules + len(nets)
            gr2.add_edge(v, num_modules + i_net)

    net_weight2 = {}
    # net_weight2.set_start(num_modules)
    for net, wt in net_weight.items():
        if net in removelist:
            continue
        net_weight2[net_up_map2[net]] = wt

    net_weight.clear()  # no moe net_weight
    net_up_map2.clear()  # no more net_up_map2
    removelist.clear()  # no more updaed_nets

    hgr2 = HierNetlist(gr2, range(num_modules),
                       range(num_modules, num_modules + num_nets))

    node_down_list = [0] * num_modules
    for v1, v2 in node_up_dict.items():
        node_down_list[v2] = v1
    node_up_dict.clear()  # no more node_up_dict

    # cluster_down_map = {node_up_dict[v]: netk
    #                     for netk in s1 for v in hgr.gr[netk]}
    # cluster_down_map = {module_map[net]: net for net in clusters}

    module_weight2 = [0] * num_modules
    num_cells = num_modules - num_clusters
    for v, v2 in enumerate(node_down_list):
        # TODO: take only first num_cells items
        module_weight2[v] = module_weight[v2]
    for i_v, net in enumerate(clusters):
        module_weight2[num_cells + i_v] = cluster_weight[net]

    # for i_v in range(num_modules):
    #     if i_v in cluster_down_map:
    #         net = cluster_down_map[i_v]
    #         module_weight2[i_v] = cluster_weight[net]
    #     else:
    #         v2 = node_down_list[i_v]
    #         module_weight2[i_v] = module_weight[v2]

    hgr2.clusters = clusters
    hgr2.num_clusters = num_clusters
    hgr2.node_down_list = node_down_list
    # hgr2.cluster_down_map = cluster_down_map
    hgr2.module_weight = module_weight2
    hgr2.net_weight = net_weight2
    hgr2.parent = hgr
    return hgr2, module_weight2


def purge_duplicate_nets(hgr, gr, nets, num_clusters, num_modules):
    # Purging duplicate nets
    # num_modules = len(module_map)
    num_nets = len(nets)
    net_weight = {}
    # net_weight.set_start(num_modules)
    for i_net, net in enumerate(nets):
        wt = hgr.get_net_weight(net)
        if wt != 1:
            net_weight[num_modules + i_net] = wt

    removelist = set()
    # for net in clusters:
    #     cluster = module_map[net]
    for cluster in range(num_modules - num_clusters, num_modules):
        for net1 in gr[cluster]:  # only check the nets of cluster
            assert net1 >= num_modules
            assert net1 < num_modules + num_nets
            if gr.degree(net1) == 1:  # self loop
                removelist.add(net1)
                continue
            for net2 in filter(lambda net2: net2 != net1, gr[cluster]):
                if gr.degree(net1) != gr.degree(net2):
                    continue  # no need to check if pins are different
                same = False
                # TODO: consider to use MinHash to check for more nets
                if gr.degree(net1) <= 3:  # only check for low-pin nets
                    set1 = set(v for v in gr[net1])
                    set2 = set(v for v in gr[net2])
                    if set1 == set2:  # expensive operation for high-pin nets
                        same = True
                if same:
                    removelist.add(net2)
                    net_weight[net1] = net_weight.get(
                        net1, 1) + net_weight.get(net2, 1)
    # gr.remove_nodes_from(removelist)
    # original_net = range(num_modules, num_modules + num_nets)
    # updated_nets = set(net for net in original_net if net not in removelist)
    return net_weight, removelist
