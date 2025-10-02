"""
Clustering Algorithm

This code implements a clustering algorithm for graph contraction, which is used in circuit design and optimization. The main purpose of this code is to simplify a complex graph (called a hypergraph) by grouping together certain nodes (called modules) into clusters. This process helps in reducing the complexity of the graph while maintaining its essential structure.

The code takes as input a hypergraph (represented by the Netlist class), weights for modules and clusters, and a set of forbidden nets (connections that should not be grouped). It produces as output a new, simplified graph (called a hierarchical netlist) with updated weights for the modules.

The algorithm works through several steps to achieve its purpose:

1. It starts by finding a minimum maximal matching in the graph, which is a way of pairing up nodes that are connected.

2. Then, it sets up the initial clusters, nets, and cell list based on this matching.

3. Next, it constructs a new graph based on these clusters and remaining nodes.

4. The code then purges duplicate nets, which are connections that essentially represent the same thing. This step helps further simplify the graph.

5. After purging duplicates, it reconstructs the graph with the updated information.

6. Finally, it contracts the subgraph, which means it combines the clustered nodes into single units in the new graph.

Throughout this process, the code keeps track of weights for modules and nets, updating them as nodes are combined into clusters. This is important because the weights represent the importance or size of each module or connection in the graph.

The main logic flow involves transforming the original complex graph into a simpler one by grouping connected nodes, removing redundant connections, and updating the weights accordingly. This is achieved through a series of graph operations and data structure manipulations.

For a beginner programmer, it's important to understand that this code is dealing with graph theory concepts, which are used to represent complex relationships between objects. The algorithm is trying to simplify these relationships while preserving the most important information. This kind of algorithm is useful in many fields, including circuit design, network analysis, and data compression.

Notes:
    module and net should have a unique id because they treat the same node in the underlying graph.
"""

from typing import List, MutableMapping, Optional, Set, Tuple, TypeVar

from netlistx.netlist import Netlist, TinyGraph
from netlistx.netlist_algo import min_maximal_matching

from .HierNetlist import HierNetlist

LOW_PIN_NET_THRESHOLD = 5
Node = TypeVar("Node")  # Hashable


def setup(
    hyprgraph: Netlist, cluster_weight: MutableMapping, forbid: Optional[Set]
) -> Tuple[List, List, List]:
    """
    The `setup` function takes in a hypergraph `hyprgraph`, cluster weights `cluster_weight`, and a set of
    forbidden dependencies `forbid`, and returns a tuple containing the clusters, nets, and cell list.

    This function performs the initial setup for clustering by:
    1. Finding a minimum maximal matching in the hypergraph
    2. Creating clusters from the matched nets
    3. Separating remaining nets that weren't clustered
    4. Collecting cells that weren't included in any clusters

    :param hyprgraph: The parameter "hyprgraph" is likely an input graph or hypergraph. It represents the
        connections between cells or nodes in a system
    :type hyprgraph: Netlist
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
            covered.update(v for v in hyprgraph.ugraph[net])
        else:
            nets.append(net)

    cell_list = [v for v in hyprgraph if v not in covered]
    return clusters, nets, cell_list


def construct_graph(hyprgraph: Netlist, nets, cell_list, clusters):
    """
    The function constructs a bipartite graph based on a given hypergraph, netlist, cell list, and
    clusters.

    This function creates a new graph representation where:
    - Modules (both individual cells and clusters) are on one side
    - Nets are on the other side
    - Edges connect modules to the nets they participate in

    :param hyprgraph: The parameter `hyprgraph` is likely an object representing a hypergraph. It is used to access
        the connections between cells and nets
    :type hyprgraph: Netlist
    :param nets: The `nets` parameter is a list of nets. Each net is represented as a list of cells that
        are connected by the net. For example, if there are two nets, the `nets` parameter could be:
    :param cell_list: The `cell_list` parameter is a list of cells in the circuit. Each cell represents
        a component or module in the circuit design
    :param clusters: clusters is a list of clusters, where each cluster is a set of cells that are
        grouped together
    :return: a bipartite graph (ugraph) that represents the connections between modules (cell_list and
        clusters) and nets.
    """
    num_modules = len(cell_list) + len(clusters)
    # Construct a graph for the next level's netlist
    num_cell = len(cell_list)
    node_up_map = {
        v: i_v + num_cell
        for i_v, net in enumerate(clusters)
        for v in hyprgraph.ugraph[net]
    }
    node_up_map.update({v: i_v for i_v, v in enumerate(cell_list)})
    ugraph = TinyGraph()  # ugraph is a bipartite graph
    ugraph.init_nodes(num_modules + len(nets))
    for i_net, net in enumerate(nets):
        for v in hyprgraph.ugraph[net]:
            ugraph.add_edge(node_up_map[v], i_net + num_modules)
            # automatically merge the same cell-net
    return ugraph


def purge_duplicate_nets(hyprgraph: Netlist, ugraph, nets, num_clusters, num_modules):
    """
    The function `purge_duplicate_nets` removes duplicate nets from a graph and returns the updated net
    weights and list of nets.

    This function identifies and removes duplicate nets by:
    1. Checking for nets that connect exactly the same set of modules
    2. For low-pin nets (<= 5 connections), it does exact set comparison
    3. Combining weights of duplicate nets into a single representative net

    :param hyprgraph: The `hyprgraph` parameter is an object that represents a hypergraph. It likely has methods to
        access information about the hypergraph, such as the weight of a net
    :type hyprgraph: Netlist
    :param ugraph: The variable `ugraph` represents a graph where each node represents a cluster and each edge
        represents a net connecting two clusters. The graph `ugraph` is represented as an adjacency list, where
        `ugraph[cluster]` returns a list of nets connected to the cluster
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
        for net1 in ugraph[cluster]:  # only check the nets of cluster
            assert net1 >= num_modules
            assert net1 < num_modules + num_nets
            if ugraph.degree(net1) == 1:  # self loop
                removelist.add(net1)
                continue
            for net2 in filter(lambda net2: net2 != net1, ugraph[cluster]):
                if ugraph.degree(net1) != ugraph.degree(net2):
                    continue  # no need to check if pins are different
                same = False
                # TODO: consider to use MinHash to check for more nets
                if ugraph.degree(net1) <= LOW_PIN_NET_THRESHOLD:
                    # only check for low-pin nets
                    set1 = set(v for v in ugraph[net1])
                    set2 = set(v for v in ugraph[net2])
                    if set1 == set2:  # expensive operation for high-pin nets
                        same = True
                if same:
                    removelist.add(net2)
                    net_weight[net1] = net_weight.get(net1, 1) + net_weight.get(net2, 1)
    # ugraph.remove_nodes_from(removelist)
    print("removed {} nets".format(len(removelist)))
    gr_nets = range(num_modules, num_modules + len(nets))
    updated_nets = [net for net in gr_nets if net not in removelist]
    return net_weight, updated_nets


def reconstruct_graph(hyprgraph: Netlist, ugraph, nets, num_clusters, num_modules):
    """
    The function reconstructs a new graph by purging duplicate nets and updating net weights.

    This function:
    1. Calls purge_duplicate_nets to identify and remove duplicate connections
    2. Creates a new graph with only the unique nets
    3. Preserves the weights of the remaining nets

    :param hyprgraph: The `hyprgraph` parameter is a hypergraph representation of the graph. It is a dictionary
        where the keys are the nodes of the graph and the values are the hyperedges that the node belongs to
    :type hyprgraph: Netlist
    :param ugraph: ugraph is a dictionary that represents the connections between modules and nets in the
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
        hyprgraph, ugraph, nets, num_clusters, num_modules
    )
    # Reconstruct a new graph with purged nets
    num_nets = len(updated_nets)
    gr2 = TinyGraph()
    gr2.init_nodes(num_modules + num_nets)
    for i_net, net in enumerate(updated_nets):
        for v in ugraph[net]:
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

    This is the main function that orchestrates the entire clustering process by:
    1. Calculating initial cluster weights
    2. Setting up initial clusters and nets
    3. Constructing the intermediate graph
    4. Purging duplicates and reconstructing the final graph
    5. Creating the hierarchical netlist structure with updated weights

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
        net: sum(module_weight[v] for v in hyprgraph.ugraph[net])
        for net in hyprgraph.nets
    }  # can be done in parallel

    clusters, nets, cell_list = setup(hyprgraph, cluster_weight, forbid)
    # Construct a graph for the next level's netlist
    ugraph = construct_graph(hyprgraph, nets, cell_list, clusters)

    num_modules = len(cell_list) + len(clusters)
    num_clusters = len(clusters)

    gr2, net_weight2, num_nets = reconstruct_graph(
        hyprgraph, ugraph, nets, num_clusters, num_modules
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
    node_down_list += [next(iter(hyprgraph.ugraph[net])) for net in clusters]

    hgr2.clusters = clusters
    hgr2.node_down_list = node_down_list
    hgr2.module_weight = module_weight2
    hgr2.net_weight = net_weight2
    hgr2.parent = hyprgraph
    return hgr2, module_weight2
