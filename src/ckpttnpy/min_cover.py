from typing import Set

# import networkx as nx

from .HierNetlist import HierNetlist
from .netlist import Netlist, TinyGraph
# from .array_like import shift_array
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

    node_up_dict, clusters, nets, cell_list = setup(hgr, cluster_weight, forbid)

    num_modules = len(cell_list) + len(clusters)
    num_clusters = len(clusters)

    # Construct a graph for the next level's netlist
    gr = TinyGraph()  # gr is a bipartite graph
    gr.init_nodes(num_modules + len(nets))
    for i_net, net in enumerate(nets):
        for v in hgr.gr[net]:
            gr.add_edge(node_up_dict[v], i_net + num_modules)
            # automatically merge the same cell-net
    node_up_dict.clear()  # no more node_up_dict

    # Purging duplicate nets
    net_weight, updated_nets = purge_duplicate_nets(
        hgr, gr, nets, num_clusters, num_modules)

    # Reconstruct a new graph with purged nets
    num_nets = len(updated_nets)
    gr2 = TinyGraph()
    gr2.init_nodes(num_modules + num_nets)
    for i_net, net in enumerate(updated_nets):
        for v in gr[net]:
            assert net >= num_modules
            assert net < num_modules + len(nets)
            gr2.add_edge(v, num_modules + i_net)

    # Update net weight
    net_weight2 = {}
    for i_net, net in enumerate(updated_nets):
        if net not in net_weight:
            continue
        net_weight2[i_net] = net_weight[net]
    net_weight.clear()  # no moe net_weight

    hgr2 = HierNetlist(gr2, range(num_modules),
                       range(num_modules, num_modules + num_nets))

    # Update module_weight
    module_weight2 = [0] * num_modules
    num_cells = num_modules - num_clusters
    for v, v2 in enumerate(cell_list):
        module_weight2[v] = module_weight[v2]
    for i_v, net in enumerate(clusters):
        module_weight2[num_cells + i_v] = cluster_weight[net]

    hgr2.clusters = clusters
    hgr2.cell_list = cell_list
    hgr2.module_weight = module_weight2
    hgr2.net_weight = net_weight2
    hgr2.parent = hgr
    return hgr2, module_weight2


def setup(hgr, cluster_weight, forbid):
    s1 = set()  # initially no preferrence
    min_maximal_matching(hgr, cluster_weight, s1, forbid)

    module_up_map: dict = {v: v for v in hgr}  # initially map to itself
    covered = set()
    nets = list()
    clusters = list()
    for net in hgr.nets:
        if net in s1:
            clusters.append(net)
            module_up_map.update({v: net for v in hgr.gr[net]})
            covered.update(v for v in hgr.gr[net])
        else:
            nets.append(net)

    cell_list = [v for v in hgr if v not in covered]
    modules = cell_list + clusters
    module_map = {v: i_v for i_v, v in enumerate(modules)}
    node_up_dict = {v: module_map[module_up_map[v]] for v in hgr}
    return node_up_dict, clusters, nets, cell_list


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
    gr_nets = range(num_modules, num_modules + len(nets))
    updated_nets = [net for net in gr_nets if net not in removelist]
    return net_weight, updated_nets
