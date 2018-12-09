# include <LEDA/core/list.h>
# include <LEDA/graph/graph.h>
# include <cassert>
# include <queue>
from .netlist import Netlist
import numpy as np

#
# Primal-dual algorithm for minimum vertex cover problem
#


def min_net_cover_pd(H, weight):
    is_covered = set()
    S = set()
    gap = weight.copy()

    total_primal_cost = 0
    total_dual_cost = 0
    offset = H.number_of_modules()

    for v in range(H.number_of_modules()):
        if v in is_covered:
            continue
        min_gap = 10000000
        i_s = 0
        for net in H.G[v]:
            i_net = net - offset
            if min_gap > gap[i_net]:
                i_s = i_net
                min_gap = gap[i_net]
        # is_net_cover[i_s] = True
        # S.append(i_s)
        S.add(i_s)
        for net in H.G[v]:
            i_net = net - offset
            gap[i_net] -= min_gap
        assert gap[i_s] == 0
        for v2 in H.G[i_s + offset]:
            is_covered.add(v2)
        total_primal_cost += weight[i_s]
        total_dual_cost += min_gap

    # for net in S:
    #     found = False
    #     leda:: node w
    #     forall_adj_nodes(w, v):
    #         if not is_net_cover[w]:
    #             found = True
    #             break

    #     if not found:
    #         S.del_item(it)
    #         total_primal_cost -= weight[v]
    #         is_net_cover[v] = False

    assert total_primal_cost >= total_dual_cost
    return S, total_primal_cost
