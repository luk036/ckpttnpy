"""
Notes:
    module and net should have a unique id because
    they treat the same node in the underlying graph.
"""
from .HierNetlist import HierNetlist
from .netlist import Netlist, TinyGraph
import copy
from typing import Union, Set, Tuple, Optional
from collections.abc import MutableMapping


def min_maximal_matching(
    hgr, weight: MutableMapping, matchset: Optional[Set] = None,
    dep: Optional[Set] = None
) -> Tuple[Set, Union[int, float]]:
    """Perform minimum weighted maximal matching using primal-dual
    approximation algorithm

    Returns:
        [type]: [description]
    """
    if matchset is None:
        matchset = set()
    if dep is None:
        dep = set()

    def cover(net):
        for vtx in hgr.gra[net]:
            dep.add(vtx)

    def any_of_dep(net):
        return any(vtx in dep for vtx in hgr.gra[net])

    total_primal_cost = 0
    total_dual_cost = 0

    gap = copy.copy(weight)
    for net in hgr.nets:
        if any_of_dep(net):
            continue
        if net in matchset:  # pre-define matching
            # cover(net)
            continue
        min_val = gap[net]
        min_net = net
        for vtx in hgr.gra[net]:
            for net2 in hgr.gra[vtx]:
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
        for vtx in hgr.gra[net]:
            for net2 in hgr.gra[vtx]:
                # if net2 == net:
                #     continue
                gap[net2] -= min_val

    assert total_dual_cost <= total_primal_cost
    return matchset, total_primal_cost


# def min_maximal_matching_old(hgr, weight, matchset, dep):
#     """Perform minimum weighted maximal matching
#        using primal-dual approximation algorithm

#     Returns:
#         [type]: [description]
#     """

#     def cover(net):
#         for v in hgr.gra[net]:
#             dep.add(v)

#     def any_of_dep(net):
#         return any(v in dep for v in hgr.gra[net])

#     gap = weight.copy()
#     total_primal_cost = 0
#     total_dual_cost = 0
#     for net in filter(lambda net: not (any_of_dep(net) or (net in matchset)),
#                       hgr.nets):
#         min_val = gap[net]
#         min_net = net
#         for v in hgr.gra[net]:
#             for net2 in filter(lambda net2: not any_of_dep(net2), hgr.gra[v]):
#                 if min_val > gap[net2]:
#                     min_val = gap[net2]
#                     min_net = net2
#         cover(min_net)
#         matchset.add(min_net)
#         total_primal_cost += weight[min_net]
#         total_dual_cost += min_val
#         if min_net == net:
#             continue
#         gap[net] -= min_val
#         for v in hgr.gra[net]:
#             for net2 in hgr.gra[v]:
#                 # if net2 == net:
#                 #     continue
#                 gap[net2] -= min_val
#     assert total_dual_cost <= total_primal_cost
#     return total_primal_cost


def contract_subgraph(hgr: Netlist, module_weight, forbid: Set):
    """[summary]

    Args:
        hgr (Netlist): [description]
        forbid (Set): [description]

    Returns:
        HierNetlist: [description]
    """
    cluster_weight = {
        net: sum(module_weight[v] for v in hgr.gra[net]) for net in hgr.nets
    }  # can be done in parallel

    clusters, nets, cell_list = setup(hgr, cluster_weight, forbid)
    # Construct a graph for the next level's netlist
    gra = construct_graph(hgr, nets, cell_list, clusters)

    num_modules = len(cell_list) + len(clusters)
    num_clusters = len(clusters)

    gr2, net_weight2, num_nets = reconstruct_graph(
        hgr, gra, nets, num_clusters, num_modules
    )

    nets.clear()  # no more nets

    hgr2 = HierNetlist(
        gr2, range(num_modules), range(num_modules, num_modules + num_nets)
    )

    # Update module_weight
    module_weight2 = [0] * num_modules
    num_cells = num_modules - num_clusters
    for v, v2 in enumerate(cell_list):
        module_weight2[v] = module_weight[v2]
    for i_v, net in enumerate(clusters):
        module_weight2[num_cells + i_v] = cluster_weight[net]

    node_down_list = cell_list
    node_down_list += [next(iter(hgr.gra[net])) for net in clusters]

    hgr2.clusters = clusters
    hgr2.node_down_list = node_down_list
    hgr2.module_weight = module_weight2
    hgr2.net_weight = net_weight2
    hgr2.parent = hgr
    return hgr2, module_weight2


def setup(hgr, cluster_weight, forbid):
    s1, _ = min_maximal_matching(hgr, cluster_weight, dep=forbid)
    covered = set()
    nets = list()
    clusters = list()
    for net in hgr.nets:
        if net in s1:
            clusters.append(net)
            covered.update(v for v in hgr.gra[net])
        else:
            nets.append(net)

    cell_list = [v for v in hgr if v not in covered]
    return clusters, nets, cell_list


def construct_graph(hgr, nets, cell_list, clusters):
    num_modules = len(cell_list) + len(clusters)
    # Construct a graph for the next level's netlist
    num_cell = len(cell_list)
    node_up_map = {
        v: i_v + num_cell for i_v, net in enumerate(clusters) for v in hgr.gra[net]
    }
    node_up_map.update({v: i_v for i_v, v in enumerate(cell_list)})
    gra = TinyGraph()  # gra is a bipartite graph
    gra.init_nodes(num_modules + len(nets))
    for i_net, net in enumerate(nets):
        for v in hgr.gra[net]:
            gra.add_edge(node_up_map[v], i_net + num_modules)
            # automatically merge the same cell-net
    return gra


def reconstruct_graph(hgr, gra, nets, num_clusters, num_modules):
    # Purging duplicate nets
    net_weight, updated_nets = purge_duplicate_nets(
        hgr, gra, nets, num_clusters, num_modules
    )
    # Reconstruct a new graph with purged nets
    num_nets = len(updated_nets)
    gr2 = TinyGraph()
    gr2.init_nodes(num_modules + num_nets)
    for i_net, net in enumerate(updated_nets):
        for v in gra[net]:
            assert net >= num_modules
            assert net < num_modules + len(nets)
            gr2.add_edge(v, num_modules + i_net)
    # Update net weight
    net_weight2 = {}
    for i_net, net in enumerate(updated_nets):
        if net not in net_weight:
            continue
        net_weight2[i_net] = net_weight[net]
    return gr2, net_weight2, num_nets


def purge_duplicate_nets(hgr, gra, nets, num_clusters, num_modules):
    # Purging duplicate nets
    num_nets = len(nets)
    net_weight = {}
    # net_weight.set_start(num_modules)
    for i_net, net in enumerate(nets):
        wt = hgr.get_net_weight(net)
        if wt != 1:
            net_weight[num_modules + i_net] = wt

    removelist = set()
    for cluster in range(num_modules - num_clusters, num_modules):
        for net1 in gra[cluster]:  # only check the nets of cluster
            assert net1 >= num_modules
            assert net1 < num_modules + num_nets
            if gra.degree(net1) == 1:  # self loop
                removelist.add(net1)
                continue
            for net2 in filter(lambda net2: net2 != net1, gra[cluster]):
                if gra.degree(net1) != gra.degree(net2):
                    continue  # no need to check if pins are different
                same = False
                # TODO: consider to use MinHash to check for more nets
                if gra.degree(net1) <= 5:  # magic number!
                    # only check for low-pin nets
                    set1 = set(v for v in gra[net1])
                    set2 = set(v for v in gra[net2])
                    if set1 == set2:  # expensive operation for high-pin nets
                        same = True
                if same:
                    removelist.add(net2)
                    net_weight[net1] = net_weight.get(
                        net1, 1) + net_weight.get(net2, 1)
    # gra.remove_nodes_from(removelist)
    print("removed {} nets".format(len(removelist)))
    gr_nets = range(num_modules, num_modules + len(nets))
    updated_nets = [net for net in gr_nets if net not in removelist]
    return net_weight, updated_nets
