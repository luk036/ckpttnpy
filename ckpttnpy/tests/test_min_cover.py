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
    if H.net_weight == {}:
        gap = list(1 for _ in range(H.number_of_nets()))
    else:
        gap = H.net_weight.copy()
    # gap = weight.copy()

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
        total_primal_cost += H.get_net_weight(i_s + offset)
        total_dual_cost += min_gap

    assert total_primal_cost >= total_dual_cost

    S2 = S.copy()
    for net in S2:
        found = False
        for v in H.G[net]:
            covered = False
            for net2 in H.G[v]:
                if net2 == net:
                    continue
                if net2 in S:
                    covered = True
            if not covered:
                found = True
                break
        if found:
            continue
        total_primal_cost -= H.get_net_weight(net)
        S.remove(net)

    return total_primal_cost


def test_min_net_cover_pd():
    # random_graph(G,5,20)
    H = create_drawf()
    _, cost1 = min_net_cover_pd(H, H.net_weight)
    assert cost1 == 3


if __name__ == "__main__":
    test_min_net_cover_pd()
