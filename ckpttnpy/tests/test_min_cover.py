from ckpttnpy.min_cover import min_net_cover_pd
from ckpttnpy.tests.test_netlist import create_drawf

from ckpttnpy.netlist import Netlist

#
# Primal-dual algorithm for minimum vertex cover problem
#


def min_net_cover_pd2(H, weight):
    is_covered = {}
    is_net_cover = {}
    S = []
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
        is_net_cover[i_s] = True
        S.append(i_s)
        for net in H.G[v]:
            i_net = net - offset
            gap[i_net] -= min_gap
        assert gap[i_s] == 0
        for v2 in H.G[i_s + offset]:
            is_covered[v2] = True
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
    return total_primal_cost


def test_min_net_cover_pd():
    # random_graph(G,5,20)
    H = create_drawf()
    _, cost1 = min_net_cover_pd(H, H.net_weight)
    print("total cost = ", cost1)

if __name__ == "__main__":
    test_min_net_cover_pd()