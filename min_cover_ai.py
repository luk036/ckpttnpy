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

import copy
import networkx as nx

from typing import List, MutableMapping, Optional, Set, Tuple, TypeVar, Union
from typing import Any
from typing import Iterator

T = TypeVar("T")


class MapAdapter(MutableMapping[int, T]):
    """MapAdapter

    The `MapAdapter` class is a custom implementation of a mutable mapping with integer keys and generic
    values, which adapts a list to behave like a dictionary.
    """

    def __init__(self, lst: List[T]) -> None:
        """
        The function is a constructor for a dictionary-like adaptor for a list.

        :param lst: The `lst` parameter is a list that is being passed to the `__init__` method. It is used to initialize the `self.lst` attribute of the class
        :type lst: List[T]
        """
        self.lst = lst

    def __getitem__(self, key: int) -> T:
        """
        This function allows you to access an element in a MapAdapter object by its index.

        :param key: The `key` parameter is of type `int` and it represents the index of the element that you want to retrieve from the list
        :type key: int
        :return: The `__getitem__` method is returning the item at the specified index in the `lst` attribute.

        Examples:
            >>> a = MapAdapter([1, 4, 3, 6])
            >>> a[2]
            3
        """
        return self.lst.__getitem__(key)

    def __setitem__(self, key: int, new_value: T):
        """
        This function sets the value at a given index in a list-like object.

        :param key: The key parameter represents the index at which the new value should be set in the list
        :type key: int
        :param new_value: The `new_value` parameter is the value that you want to assign to the element at the specified key in the list
        :type new_value: T

        Examples:
            >>> a = MapAdapter([1, 4, 3, 6])
            >>> a[2] = 7
            >>> print(a[2])
            7
        """
        self.lst.__setitem__(key, new_value)

    def __delitem__(self, _):
        """
        The __delitem__ function raises a NotImplementedError and provides a docstring explaining that
        deleting items from MapAdapter is not recommended.

        :param _: The underscore (_) is typically used as a placeholder for a variable or value that is not going to be used or referenced in the code. In this case, it is used as a placeholder for the key parameter in the __delitem__ method
        """
        raise NotImplementedError()

    def __iter__(self) -> Iterator:
        """
        The function returns an iterator that yields elements from the `rng` attribute of the object.

        :return: The `iter(self.rng)` is being returned.

        Examples:
            >>> a = MapAdapter([1, 4, 3, 6])
            >>> for i in a:
            ...     print(i)
            0
            1
            2
            3
        """
        return iter(range(len(self.lst)))

    def __contains__(self, value) -> bool:
        """
        The `__contains__` function checks if a given value is present in the `rng` attribute of the object.

        :param value: The `value` parameter represents the value that we want to check if it is present in the `self.rng` attribute
        :return: The method is returning a boolean value, indicating whether the given value is present in the `self.rng` attribute.

        Examples:
            >>> a = MapAdapter([1, 4, 3, 6])
            >>> 2 in a
            True
        """
        return value < len(self.lst) and value >= 0

    def __len__(self) -> int:
        """
        This function returns the length of the `rng` attribute of the object.
        :return: The `len` function is returning the length of the `self.rng` attribute.

        Examples:
            >>> a = MapAdapter([1, 4, 3, 6])
            >>> len(a)
            4
        """
        return len(self.lst)

    def values(self):
        """
        The `values` function returns an iterator that yields the elements of the `lst` attribute of the
        `MapAdapter` object.

        :return: The `values` method returns an iterator object.

        Examples:
            >>> a = MapAdapter([1, 4, 3, 6])
            >>> for i in a.values():
            ...     print(i)
            1
            4
            3
            6
        """
        return iter(self.lst)

    def items(self):
        """
        The function returns an enumeration of the items in the list.

        :return: The `items` method is returning an enumeration of the `lst` attribute.
        """
        return enumerate(self.lst)


class TinyGraph(nx.Graph):
    num_nodes = 0

    def cheat_node_dict(self):
        return MapAdapter([dict() for _ in range(self.num_nodes)])

    def cheat_adjlist_outer_dict(self):
        return MapAdapter([dict() for _ in range(self.num_nodes)])

    node_dict_factory = cheat_node_dict
    adjlist_outer_dict_factory = cheat_adjlist_outer_dict

    def init_nodes(self, n: int):
        self.num_nodes = n
        self._node = self.cheat_node_dict()
        self._adj = self.cheat_adjlist_outer_dict()
        # self._pred = self.cheat_adjlist_outer_dict()


from itertools import repeat


class RepeatArray:
    """The RepeatArray class creates a list-like object that repeats a given value for a specified number
    of times."""

    def __init__(self, value, size):
        """
        The function initializes an object with a value and size attribute.

        :param value: The value parameter is used to store the value of an object. It can be of any data type, such as an integer, string, or even another object
        :param size: The `size` parameter represents the size of an object or data structure.

        Examples:
            >>> repeat_array = RepeatArray(1, 5)
            >>> repeat_array.value
            1
            >>> repeat_array.size
            5

        """
        self.value = value
        self.size = size

    def __getitem__(self, _):  # key is ignored
        """
        The `__getitem__` function returns the value of the object regardless of the key provided.

        :param _: The parameter "_" in the __getitem__ method is used to indicate that the key argument is
                  ignored. It is a convention in Python to use "_" as a placeholder for variables that are not used or
                  not important in a particular context. In this case, the key argument is not used in the method implementation

        :return: The value stored in the `self.value` attribute.

        Examples:
            >>> repeat_array = RepeatArray(1, 5)
            >>> repeat_array[0]
            1
            >>> repeat_array[1]
            1
            >>> repeat_array[2]
            1
            >>> repeat_array[3]
            1
            >>> repeat_array[4]
            1

        """
        return self.value

    def __len__(self):
        """
        The function returns the size of an object.

        :return: The size of the object.

        Examples:
            >>> repeat_array = RepeatArray(1, 5)
            >>> len(repeat_array)
            5

        """
        return self.size

    def __iter__(self):
        """
        The function returns an iterator that repeats the value of the object a specified number of times.

        :return: The `repeat` function is being returned.

        Examples:
            >>> repeat_array = RepeatArray(1, 5)
            >>> for i in repeat_array:
            ...     print(i)
            1
            1
            1
            1
            1
        """
        return repeat(self.value, self.size)

    def get(self, _):  # defaultvalue is ignored
        """
        The `get` function returns the value of the object.

        :param _: The underscore (_) is a convention in Python to indicate that a parameter is not going to
                  be used in the function. In this case, the parameter is ignored and not used in the function logic

        :return: The value of the `self.value` attribute is being returned.

        Examples:
            >>> repeat_array = RepeatArray(1, 5)
            >>> repeat_array.get(0)
            1
            >>> repeat_array.get(1)
            1
            >>> repeat_array.get(2)
            1
            >>> repeat_array.get(3)
            1
            >>> repeat_array.get(4)
            1

        """
        return self.value


# The `Netlist` class represents a netlist, which is a collection of modules and nets in a graph
# structure, and provides various properties and methods for working with the netlist.
class Netlist:
    num_pads = 0
    cost_model = 0

    def __init__(
        self,
        ugraph: nx.Graph,
        modules: Union[range, List[Any]],
        nets: Union[range, List[Any]],
    ):
        """
        The function initializes an object with a graph, modules, and nets, and calculates some properties
        of the graph.

        :param ugraph: The parameter `ugraph` is a graph object of type `nx.Graph`. It represents the graph
            structure of the system
        :type ugraph: nx.Graph
        :param modules: The `modules` parameter is a list or range object that represents the modules in the
            graph. Each module is a node in the graph
        :type modules: Union[range, List[Any]]
        :param nets: The `nets` parameter is a list or range that represents the nets in the graph. A net is
            a connection between two or more modules
        :type nets: Union[range, List[Any]]
        """
        self.ugraph = ugraph
        self.modules = modules
        self.nets = nets

        self.num_modules = len(modules)
        self.num_nets = len(nets)
        # self.net_weight: Optional[Union[Dict, List[int]]] = None
        self.module_weight = RepeatArray(1, self.num_modules)
        self.module_fixed: set = set()

        # self.module_dict = {}
        # for v in enumerate(self.module_list):
        #     self.module_dict[v] = v

        # self.net_dict = {}
        # for i_net, net in enumerate(self.net_list):
        #     self.net_dict[net] = i_net

        # self.module_fixed = module_fixed
        # self.has_fixed_modules = (self.module_fixed != [])
        self.max_degree = max(self.ugraph.degree[cell] for cell in modules)
        # self.max_net_degree = max(self.ugraph.degree[net] for net in nets)

    def number_of_modules(self) -> int:
        """
        The function "number_of_modules" returns the number of modules.
        :return: The method is returning the value of the attribute `num_modules`.
        """
        return self.num_modules

    def number_of_nets(self) -> int:
        """
        The function "number_of_nets" returns the number of nets.
        :return: The number of nets.
        """
        return self.num_nets

    def number_of_nodes(self) -> int:
        """
        The function "number_of_nodes" returns the number of nodes in a graph.
        :return: The number of nodes in the graph.
        """
        return self.ugraph.number_of_nodes()

    def number_of_pins(self) -> int:
        """
        The function `number_of_pins` returns the number of edges in a graph.
        :return: The number of edges in the graph.
        """
        return self.ugraph.number_of_edges()

    def get_max_degree(self) -> int:
        """
        The function `get_max_degree` returns the maximum degree of nodes in a graph.
        :return: the maximum degree of the nodes in the graph.
        """
        return max(self.ugraph.degree[cell] for cell in self.modules)

    def get_module_weight(self, v) -> int:
        """
        The function `get_module_weight` returns the weight of a module given its index.

        :param v: The parameter `v` in the `get_module_weight` function is of type `size_t`. It represents
            the index or key of the module weight that you want to retrieve
        :return: the value of `self.module_weight[v]`.
        """
        return self.module_weight[v]

    def get_net_weight(self, _) -> int:
        """
        The function `get_net_weight` returns an integer value.

        :param _: The underscore (_) in the function signature is a convention in Python to indicate that
            the parameter is not used within the function. It is often used when a parameter is required by the
            function signature but not actually used within the function's implementation. In this case, the
            underscore (_) is used as a placeholder for
        :return: An integer value of 1 is being returned.
        """
        return 1

    def __iter__(self):
        """
        The function returns an iterator over all modules in the Netlist.
        :return: The `iter(self.modules)` is being returned.
        """
        return iter(self.modules)


Node = TypeVar("Node")  # Hashable


from netlistx.netlist import Netlist

# from typing import Mapping, MutableMapping


class HierNetlist(Netlist):
    """The `HierNetlist` class is a subclass of `Netlist` that represents a hierarchical netlist and
    includes additional attributes and methods for managing clusters and weights of nets.
    """

    parent: Netlist

    def __init__(self, ugraph: nx.Graph, modules, nets):
        """
        The function initializes an object with a graph, modules, and nets, and sets some attributes.

        :param ugraph: ugraph is a variable of type nx.Graph, which represents a graph. It is used as an argument
            in the constructor of the class
        :type ugraph: nx.Graph
        :param modules: The `modules` parameter is either a range or a list that represents the modules in
            the graph. It contains the information about the modules present in the graph
        :param nets: The `nets` parameter is either a range or a list that represents the nets in the graph.
            A net is a collection of interconnected nodes in a circuit or network
        """
        Netlist.__init__(self, ugraph, modules, nets)
        # self.parent = self
        self.node_down_list: List[Any] = []
        self.net_weight: dict = {}
        self.clusters: List[Any] = []

    def get_degree(self, v):
        """
        The function `get_degree` returns the sum of the weights of all edges connected to a given vertex.

        :param v: The parameter `v` represents a vertex in a graph
        :return: The function `get_degree` returns the sum of the values in the `net_weight` dictionary for
            each element in the `ugraph[v]` list.
        """
        return sum(self.net_weight.get(net, 1) for net in self.ugraph[v])

    def get_max_degree(self):
        """
        The function `get_max_degree` returns the maximum degree of all the modules in a graph.
        :return: the maximum degree of all the modules in the graph.
        """
        return max(self.get_degree(v) for v in self.modules)

    def projection_down(self, part, part_down):
        """
        The `projection_down` function assigns values from the `part` list to the `part_down` list based on
        the mapping defined by the `self.node_down_list` and `self.clusters` lists.

        3 3 3 2 0 2 3 4 3 1     self
        0 1 2 3 4 5 6 7 8 9,    parent

        cluster_down_map
        2   3   4
        10  13  12

        :param part: The `part` parameter is either a dictionary or a list of integers. It represents the
            partitioning of nodes in a graph
        :param part_down: The `part_down` parameter is either a dictionary or a list of integers. It
            represents the mapping of nodes in the `self.node_down_list` to their corresponding clusters in the
            `part` parameter
        """
        num_cells = len(self.node_down_list) - len(self.clusters)
        for v1, v2 in enumerate(self.node_down_list[:num_cells]):
            part_down[v2] = part[v1]
        for i_v, net in enumerate(self.clusters):
            p = part[num_cells + i_v]
            for v2 in self.parent.ugraph[net]:
                part_down[v2] = p

    def projection_up(self, part, part_up):
        """
        The `projection_up` function maps values from `part` to `part_up` based on the indices in
        `self.node_down_list`.

        :param part: The parameter `part` can be either a dictionary or a list of integers
        :param part_up: The `part_up` parameter is either a dictionary or a list of integers
        """
        for v1, v2 in enumerate(self.node_down_list):
            part_up[v1] = part[v2]

    def get_net_weight(self, net) -> int:
        """
        The function `get_net_weight` returns the net weight of a given net, with a default value of 1 if
        the net weight is not found.

        :param net: The parameter "net" in the get_net_weight method is the key used to retrieve the value
            from the net_weight dictionary
        :return: the value associated with the key 'net' in the dictionary 'self.net_weight'. If the key is
            not found in the dictionary, it will return 1.
        """
        return self.net_weight.get(net, 1)


def min_maximal_matching(
    hyprgraph: Netlist,
    weight: MutableMapping,
    matchset: Optional[Set] = None,
    dep: Optional[Set] = None,
) -> Tuple[Set, Union[int, float]]:
    r"""
    The `min_maximal_matching` function performs minimum weighted maximal matching using a primal-dual
    approximation algorithm.

    :param hyprgraph: The `hyprgraph` parameter represents a hypergraph, which is a generalization of a
        graph where an edge can connect more than two vertices. It is not clear from the code snippet what
        the exact data structure of the hypergraph is, but it likely contains information about the vertices
        and edges of

    :param weight: The `weight` parameter is a mutable mapping that represents the weights of the
        hypergraph edges. It is used to determine the weight of each edge in the matching. The keys of the
        `weight` mapping correspond to the hypergraph edges, and the values represent their weights

    :type weight: MutableMapping

    :param matchset: The `matchset` parameter is a set that represents the pre-defined matching. It
        contains the hyperedges (nets) that are already matched

    :type matchset: Optional[Set]

    :param dep: The `dep` parameter is a set that represents the set of vertices that are covered by the
        current matching. It is initially set to an empty set, and is updated during the execution of the
        algorithm

    :type dep: Optional[Set]

    :return: The function `min_maximal_matching` returns a tuple containing the matchset (a set of
        matched elements) and the total primal cost (an integer or float representing the total weight of
        the matching).

    .. svgbob::
       :align: center

        a       b        e       g
        o=======o-----+--o=======o
                      |  |
                   ,--)--'
                   |  |
                   |  `--.
                   |     |
        o=======o--+-----o=======o
        c       d        f       h

    """
    if matchset is None:
        matchset = set()
    if dep is None:
        dep = set()

    def cover(net):
        for vtx in hyprgraph.ugraph[net]:
            dep.add(vtx)

    def any_of_dep(net):
        return any(vtx in dep for vtx in hyprgraph.ugraph[net])

    total_prml_cost = 0
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
        for vtx in hyprgraph.ugraph[net]:
            for net2 in hyprgraph.ugraph[vtx]:
                if any_of_dep(net2):
                    continue
                if min_val > gap[net2]:
                    min_val = gap[net2]
                    min_net = net2
        cover(min_net)
        matchset.add(min_net)
        total_prml_cost += weight[min_net]
        total_dual_cost += min_val
        if min_net == net:
            continue
        gap[net] -= min_val
        for vtx in hyprgraph.ugraph[net]:
            for net2 in hyprgraph.ugraph[vtx]:
                # if net2 == net:
                #     continue
                gap[net2] -= min_val

    assert total_dual_cost <= total_prml_cost
    return matchset, total_prml_cost


def setup(
    hyprgraph: Netlist, cluster_weight: MutableMapping, forbid: Optional[Set]
) -> Tuple[List, List, List]:
    """
    The `setup` function takes in a hypergraph `hyprgraph`, cluster weights `cluster_weight`, and a set of
    forbidden dependencies `forbid`, and returns a tuple containing the clusters, nets, and cell list.

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
                if ugraph.degree(net1) <= 5:  # magic number!
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
