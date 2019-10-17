import networkx as nx

from .netlist import Netlist


def max_independent_net(H, weight, DontSelect):
    """Maximal Indepentent Net

    Arguments:
        H (type):  description
        weight (type):  description

    Returns:
        dtype:  description
    """

    # bpqueue bpq{-int(H.get_max_net_degree()), 0};
    # auto nets = std::vector<dllink<int>>(H.nets.size());

    # for (auto i_net = 0U; i_net < H.nets.size(); ++i_net) {
    #     auto net = H.nets[i_net];
    #     bpq.append(nets[i_net], -H.G.degree(net));
    # }

    # net_map = {net: i_net for i_net, net in enumerate(H.nets)}

    # visited = list(False for _ in H.nets)
    visited = set()
    for net in DontSelect:
        # visited[net_map[net]] = True
        visited.add(net)

    S = set()
    total_cost = 0

    # while (!bpq.is_empty()) {
    #     dllink<int>& item = bpq.popleft();
    #     auto i_net = std::distance(&nets[0], &item);
    for net in H.nets:
        # if visited[i_net]:
        if net in visited:
            continue
        if H.G.degree(net) < 2:
            continue
        # if net in DontSelect:
        #     continue
        S.add(net)
        total_cost += H.get_net_weight(net)
        for v in H.G[net]:
            for net2 in H.G[v]:
                # i_net2 = net_map[net2]
                # visited[i_net2] = True
                visited.add(net2)
    return S, total_cost


# def min_net_cover_pd(H, weight):
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

#     for v in H.modules:
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


def create_contraction_subgraph(H, DontSelect):
    S, _ = max_independent_net(H, H.module_weight, DontSelect)

    module_up_map = {v: v for v in H.modules}
    # for v in H.modules:
    #     module_up_map[v] = v

    C = set()
    nets = []
    clusters = []
    cluster_map = {}
    for net in H.nets:
        if net in S:
            netCur = iter(H.G[net])
            master = next(netCur)
            clusters.append(master)
            for v in H.G[net]:
                module_up_map[v] = master
                C.add(v)
            cluster_map[master] = net
        else:
            nets.append(net)

    modules = [v for v in H.modules if v not in C]
    modules += clusters
    numModules = len(modules)
    numNets = len(nets)

    module_map = {v: i_v for i_v, v in enumerate(modules)}
    net_map = {net: i_net for i_net, net in enumerate(nets)}
    node_up_map = {v: module_map[module_up_map[v]] for v in H.modules}
    net_up_map = {net: net_map[net] + numModules for net in nets}
    # for net in nets:
    #     node_up_map[net] = net_map[net] + numModules
    node_up_map.update(net_up_map)

    G = nx.Graph()
    G.add_nodes_from(n for n in range(numModules + numNets))
    for v in H.modules:
        for net in H.G[v]:
            if net in S:
                continue
            G.add_edge(node_up_map[v], node_up_map[net])

    H2 = Netlist(G, range(numModules), range(numModules, numModules + numNets))

    node_down_map = {v2: v1 for v1, v2 in node_up_map.items()}
    cluster_down_map = {node_up_map[v]: net for v, net in cluster_map.items()}

    module_weight = []
    for i_v in range(numModules):
        if i_v in cluster_down_map:
            net = cluster_down_map[i_v]
            cluster_weight = 0
            for v2 in H.G[net]:
                cluster_weight += H.get_module_weight(v2)
            module_weight.append(cluster_weight)
        else:
            v2 = node_down_map[i_v]
            module_weight.append(H.get_module_weight(v2))

    H2.node_up_map = node_up_map
    H2.node_down_map = node_down_map
    H2.cluster_down_map = cluster_down_map
    H2.module_weight = module_weight
    H2.parent = H
    return H2
