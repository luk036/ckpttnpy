from ckpttnpy.min_cover import min_net_cover_pd
from ckpttnpy.tests.test_netlist import create_drawf

from ckpttnpy.netlist import Netlist

#
# Primal-dual algorithm for minimum vertex cover problem
#

def test_min_net_cover_pd():
    # random_graph(G,5,20)
    H = create_drawf()
    _, cost1 = min_net_cover_pd(H, H.net_weight)
    assert cost1 == 3


if __name__ == "__main__":
    test_min_net_cover_pd()
