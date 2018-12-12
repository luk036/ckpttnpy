# include <LEDA/core/list.h>
# include <LEDA/graph/graph.h>
# include <cassert>
# include <queue>
from .netlist import Netlist
import numpy as np

#
# Primal-dual algorithm for minimum vertex cover problem
#

def max_independent_net_pd(H, weight):
    """Maximum Indepentent Net using Primal-Dual algorithm
    
    Arguments:
        H {[type]} -- [description]
        weight {[type]} -- [description]
    
    Returns:
        [type] -- [description]
    """
    S, _ = min_net_cover_pd(H, weight)
    L = list(net for net in H.nets if net not in S)
    return L


def min_net_cover_pd(H, weight):
    """Minimum Net Cover using Primal-Dual algorithm
    
    @todo: sort cell weight to cover big cells first

    Arguments:
        H {[type]} -- [description]
        weight {[type]} -- [description]
    
    Returns:
        [type] -- [description]
    """
    covered = set()
    # S = set()
    L = list()
    if H.net_weight == {}:
        gap = list(1 for _ in H.nets)
    else:
        gap = list(w for w in H.net_weight)
    # gap = weight.copy()

    total_primal_cost = 0
    total_dual_cost = 0
    # offset = H.number_of_modules()

    for v in H.modules:
        if v in covered:
            continue
        min_gap = 10000000
        s = 0
        for net in H.G[v]:
            i_net = H.net_map[net]
            if min_gap > gap[i_net]:
                s = net
                min_gap = gap[i_net]
        # is_net_cover[i_s] = True
        # S.append(i_s)
        L.append(s)
        for net in H.G[v]:
            i_net = H.net_map[net]
            gap[i_net] -= min_gap
        assert gap[H.net_map[s]] == 0
        for v2 in H.G[s]:
            covered.add(v2)
        total_primal_cost += H.get_net_weight(s)
        total_dual_cost += min_gap

    assert total_primal_cost >= total_dual_cost

    # S2 = S.copy()
    S = set(v for v in L)
    for net in L:
        found = False
        for v in H.G[net]:
            covered = False
            for net2 in H.G[v]:
                if net2 == net:
                    continue
                if net2 in S:
                    covered = True
                    break
            if not covered:
                found = True
                break
        if found:
            continue
        total_primal_cost -= H.get_net_weight(net)
        S.remove(net)

    return S, total_primal_cost
