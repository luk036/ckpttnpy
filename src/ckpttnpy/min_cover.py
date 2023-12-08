"""
Notes:
    module and net should have a unique id because
    they treat the same node in the underlying graph.
"""
import copy
from typing import MutableMapping, Optional, Set, Tuple, Union

from .HierNetlist import HierNetlist
from .netlist import Netlist, TinyGraph


def min_maximal_matching(
    hyprgraph,
    weight: MutableMapping,
    matchset: Optional[Set] = None,
    dep: Optional[Set] = None,
) -> Tuple[Set, Union[int, float]]:
    """
    The `min_maximal_matching` function performs a minimum weighted maximal matching using a primal-dual
    approximation algorithm.

    :param hyprgraph: The `hyprgraph` parameter is an object representing a hypergraph. It likely contains
    information about the vertices and edges of the hypergraph
    :param weight: The `weight` parameter is a mutable mapping that represents the weight of each net in
    the hypergraph. It is used to determine the cost of each net in the matching
    :type weight: MutableMapping
    :param matchset: The `matchset` parameter is a set that represents the initial matching. It contains
    the nets (networks) that are already matched
    :type matchset: Optional[Set]
    :param dep: The `dep` parameter is a set that keeps track of the vertices that have been covered by
    the matching. It is initially set to an empty set, and is updated by the `cover` function. The
    `cover` function takes a net as input and adds all the vertices connected to that net
    :type dep: Optional[Set]
    :return: The function `min_maximal_matching` returns a tuple containing the matchset (a set of
    matched elements) and the total primal cost (an integer or float representing the total weight of
    the matching).
    """
    if matchset is None:
        matchset = set()
    if dep is None:
        dep = set()

    def cover(net):
        for vtx in hyprgraph.gra[net]:
            dep.add(vtx)

    def any_of_dep(net):
        return any(vtx in dep for vtx in hyprgraph.gra[net])

    total_primal_cost = 0
    total_dual_cost = 0

    gap = copy.copy(weight)
    for net in hyprgraph.nets:
        if any_of_dep(net):
            continue
        if net in matchset:  # pre-define matching
            # cover(net)
            continue
        min_val = gap[net]
        min_net = net
        for vtx in hyprgraph.gra[net]:
            for net2 in hyprgraph.gra[vtx]:
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
        for vtx in hyprgraph.gra[net]:
            for net2 in hyprgraph.gra[vtx]:
                # if net2 == net:
                #     continue
                gap[net2] -= min_val

    assert total_dual_cost <= total_primal_cost
    return matchset, total_primal_cost


# def min_maximal_matching_old(hyprgraph, weight, matchset, dep):
#     """Perform minimum weighted maximal matching
#        using primal-dual approximation algorithm

#     Returns:
#         [type]: [description]
#     """

#     def cover(net):
#         for v in hyprgraph.gra[net]:
#             dep.add(v)

#     def any_of_dep(net):
#         return any(v in dep for v in hyprgraph.gra[net])

#     gap = weight.copy()
#     total_primal_cost = 0
#     total_dual_cost = 0
#     for net in filter(lambda net: not (any_of_dep(net) or (net in matchset)),
#                       hyprgraph.nets):
#         min_val = gap[net]
#         min_net = net
#         for v in hyprgraph.gra[net]:
#             for net2 in filter(lambda net2: not any_of_dep(net2), hyprgraph.gra[v]):
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
#         for v in hyprgraph.gra[net]:
#             for net2 in hyprgraph.gra[v]:
#                 # if net2 == net:
#                 #     continue
#                 gap[net2] -= min_val
#     assert total_dual_cost <= total_primal_cost
#     return total_primal_cost


def setup(hyprgraph, cluster_weight, forbid):
    """
    The `setup` function takes in a hypergraph `hyprgraph`, cluster weights `cluster_weight`, and a set of
    forbidden dependencies `forbid`, and returns a tuple containing the clusters, nets, and cell list.

    :param hyprgraph: The parameter "hyprgraph" is likely an input graph or hypergraph. It represents the
    connections between cells or nodes in a system
    :param cluster_weight: The parameter "cluster_weight" represents the weight of each cluster in the
    hypergraph. It is used in the min_maximal_matching function to determine the matching with the
    minimum weight
    :param forbid: The `forbid` parameter is used to specify a set of vertices that should not be
    included in the matching. It is used in the `min_maximal_matching` function to ensure that the
    matching does not include certain vertices
    :return: three values: clusters, nets, and cell_list.
    """
    s1, _ = min_maximal_matching(hyprgraph, cluster_weight, dep=forbid)
    covered = set()
    nets = list()
    clusters = list()
    for net in hyprgraph.nets:
        if net in s1:
            clusters.append(net)
            covered.update(v for v in hyprgraph.gra[net])
        else:
            nets.append(net)

    cell_list = [v for v in hyprgraph if v not in covered]
    return clusters, nets, cell_list


def construct_graph(hyprgraph, nets, cell_list, clusters):
    """
    The function constructs a bipartite graph based on a given hypergraph, netlist, cell list, and
    clusters.

    :param hyprgraph: The parameter `hyprgraph` is likely an object representing a hypergraph. It is used to access
    the connections between cells and nets
    :param nets: The `nets` parameter is a list of nets. Each net is represented as a list of cells that
    are connected by the net. For example, if there are two nets, the `nets` parameter could be:
    :param cell_list: The `cell_list` parameter is a list of cells in the circuit. Each cell represents
    a component or module in the circuit design
    :param clusters: clusters is a list of clusters, where each cluster is a set of cells that are
    grouped together
    :return: a bipartite graph (gra) that represents the connections between modules (cell_list and
    clusters) and nets.
    """
    num_modules = len(cell_list) + len(clusters)
    # Construct a graph for the next level's netlist
    num_cell = len(cell_list)
    node_up_map = {
        v: i_v + num_cell
        for i_v, net in enumerate(clusters)
        for v in hyprgraph.gra[net]
    }
    node_up_map.update({v: i_v for i_v, v in enumerate(cell_list)})
    gra = TinyGraph()  # gra is a bipartite graph
    gra.init_nodes(num_modules + len(nets))
    for i_net, net in enumerate(nets):
        for v in hyprgraph.gra[net]:
            gra.add_edge(node_up_map[v], i_net + num_modules)
            # automatically merge the same cell-net
    return gra


def purge_duplicate_nets(hyprgraph, gra, nets, num_clusters, num_modules):
    """
    The function `purge_duplicate_nets` removes duplicate nets from a graph and returns the updated net
    weights and list of nets.

    :param hyprgraph: The `hyprgraph` parameter is an object that represents a hypergraph. It likely has methods to
    access information about the hypergraph, such as the weight of a net
    :param gra: The variable `gra` represents a graph where each node represents a cluster and each edge
    represents a net connecting two clusters. The graph `gra` is represented as an adjacency list, where
    `gra[cluster]` returns a list of nets connected to the cluster
    :param nets: The `nets` parameter is a list of nets. A net is a collection of pins that are
    connected together. Each net is represented by a unique identifier
    :param num_clusters: The parameter "num_clusters" represents the number of clusters in the graph
    :param num_modules: The number of modules in the graph
    :return: The function `purge_duplicate_nets` returns two values: `net_weight` and `updated_nets`.
    """
    # Purging duplicate nets
    num_nets = len(nets)
    net_weight = {}
    # net_weight.set_start(num_modules)
    for i_net, net in enumerate(nets):
        wt = hyprgraph.get_net_weight(net)
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
                    net_weight[net1] = net_weight.get(net1, 1) + net_weight.get(net2, 1)
    # gra.remove_nodes_from(removelist)
    print("removed {} nets".format(len(removelist)))
    gr_nets = range(num_modules, num_modules + len(nets))
    updated_nets = [net for net in gr_nets if net not in removelist]
    return net_weight, updated_nets


def reconstruct_graph(hyprgraph, gra, nets, num_clusters, num_modules):
    """
    The function reconstructs a new graph by purging duplicate nets and updating net weights.

    :param hyprgraph: The `hyprgraph` parameter is a hypergraph representation of the graph. It is a dictionary
    where the keys are the nodes of the graph and the values are the hyperedges that the node belongs to
    :param gra: gra is a dictionary that represents the connections between modules and nets in the
    original graph. The keys of the dictionary are the module indices, and the values are lists of net
    indices that the module is connected to
    :param nets: The `nets` parameter is a list of nets, where each net is represented as a list of
    nodes. Each node is an integer representing a module in the graph
    :param num_clusters: The parameter `num_clusters` represents the number of clusters in the graph
    :param num_modules: The number of modules in the graph
    :return: three values: `gr2`, `net_weight2`, and `num_nets`.
    """
    # Purging duplicate nets
    net_weight, updated_nets = purge_duplicate_nets(
        hyprgraph, gra, nets, num_clusters, num_modules
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

    # Update net weight (@todo: check if it is neccessary)
    net_weight2 = {}
    for i_net, net in enumerate(updated_nets):
        if net not in net_weight:
            continue
        net_weight2[i_net] = net_weight[net]

    return gr2, net_weight2, num_nets


def contract_subgraph(hyprgraph: Netlist, module_weight, forbid: Set):
    """
    The `contract_subgraph` function takes a hierarchical netlist, module weights, and a set of
    forbidden nets as input, and returns a contracted hierarchical netlist with updated module weights.

    :param hyprgraph: The `hyprgraph` parameter is a Netlist object, which represents a hierarchical graph. It
    contains information about the modules (cells) and their connections (nets) in the graph
    :type hyprgraph: Netlist
    :param module_weight: The `module_weight` parameter is a dictionary that assigns a weight to each
    module in the netlist. The weight represents the importance or size of the module
    :param forbid: The `forbid` parameter is a set that contains the nets that should not be contracted.
    These nets will remain as separate entities in the resulting hierarchical netlist
    :type forbid: Set
    :return: The function `contract_subgraph` returns a tuple containing the contracted hierarchical
    netlist (`hgr2`) and the updated module weights (`module_weight2`).
    """
    cluster_weight = {
        net: sum(module_weight[v] for v in hyprgraph.gra[net]) for net in hyprgraph.nets
    }  # can be done in parallel

    clusters, nets, cell_list = setup(hyprgraph, cluster_weight, forbid)
    # Construct a graph for the next level's netlist
    gra = construct_graph(hyprgraph, nets, cell_list, clusters)

    num_modules = len(cell_list) + len(clusters)
    num_clusters = len(clusters)

    gr2, net_weight2, num_nets = reconstruct_graph(
        hyprgraph, gra, nets, num_clusters, num_modules
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
    node_down_list += [next(iter(hyprgraph.gra[net])) for net in clusters]

    hgr2.clusters = clusters
    hgr2.node_down_list = node_down_list
    hgr2.module_weight = module_weight2
    hgr2.net_weight = net_weight2
    hgr2.parent = hyprgraph
    return hgr2, module_weight2


