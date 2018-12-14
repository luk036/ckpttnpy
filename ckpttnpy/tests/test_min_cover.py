import networkx as nx

from ckpttnpy.min_cover import min_net_cover_pd, max_independent_net_pd
from ckpttnpy.tests.test_netlist import create_drawf
from ckpttnpy.netlist import Netlist


def create_contraction_subgraph(H):
    S, _ = min_net_cover_pd(H, H.module_weight)

    module_up_map = {}
    for v in H.modules:
        module_up_map[v] = v

    C = set()
    nets = []
    clusters = []
    cluster_map = {}
    for net in H.nets:
        if net in S:
            nets.append(net)
        else:
            netCur = iter(H.G[net])
            master = next(netCur)
            clusters.append(master)
            for v in H.G[net]:
                module_up_map[v] = master
                C.add(v)
            cluster_map[master] = net

    modules = list(v for v in H.modules if v not in C)
    modules += clusters
    # nodes = modules + nets
    numModules = len(modules)
    numNets = len(nets)
    node_up_map = {}
    for i_v in range(numModules):
        node_up_map[modules[i_v]] = i_v
    for i_net in range(numNets):
        node_up_map[nets[i_net]] = i_net + numModules

    G = nx.Graph()
    G.add_nodes_from(list(n for n in range(numModules + numNets)))
    for v in H.modules:
        for net in H.G[v]:
            G.add_edge(node_up_map[v], node_up_map[net])

    # module_map = {}
    # for i_v, v in enumerate(modules):
    #     module_map[v] = i_v

    # net_map = {}
    # for i_net, net in enumerate(nets):
    #     net_map[net] = i_net

    H2 = Netlist(G, range(numModules), range(numModules, numModules + numNets),
                 range(numModules), range(-numModules, numNets))

    node_down_map = {}
    for v1, v2 in node_up_map.items():
        node_down_map[v2] = v1
    H2.node_down_map = node_down_map

    cluster_down_map = {}
    for v, net in cluster_map.items():
        cluster_down_map[node_up_map[v]] = net
    H2.cluster_down_map = cluster_down_map

    module_weight = []
    for v in range(numModules):
        if v in cluster_down_map:
            net = cluster_down_map[v]
            cluster_weight = 0
            for v2 in H.G[net]:
                cluster_weight += H.get_module_weight(v2)
            module_weight.append(cluster_weight)
        else:
            v2 = node_down_map[v]
            module_weight.append(H.get_module_weight(v2))

    H2.module_weight = module_weight
    H2.parent = H
    return H2


def test_min_net_cover_pd():
    # random_graph(G,5,20)
    H = create_drawf()
    _, cost1 = min_net_cover_pd(H, H.net_weight)
    assert cost1 == 3

    # H2 = create_contraction_subgraph(H)
    # assert H2.number_of_modules() < 7
    # assert H2.number_of_nets() == 3
    # assert H2.number_of_pins() < 13
    # assert H2.get_max_degree() >= 3
    # assert H2.get_max_net_degree() <= 3
    # assert not H.has_fixed_modules
    # assert H.get_module_weight(1) == 3


if __name__ == "__main__":
    test_min_net_cover_pd()
