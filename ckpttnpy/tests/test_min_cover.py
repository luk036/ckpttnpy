import networkx as nx

from ckpttnpy.min_cover import min_net_cover_pd, max_independent_net, create_contraction_subgraph
from ckpttnpy.tests.test_netlist import create_drawf
from ckpttnpy.netlist import Netlist


def test_min_net_cover_pd():
    # random_graph(G,5,20)
    H = create_drawf()
    _, cost1 = min_net_cover_pd(H, H.net_weight)
    assert cost1 == 3


def test_create_contraction_subgraph():
    H = create_drawf()
    H2 = create_contraction_subgraph(H, set())
    H3 = create_contraction_subgraph(H2, set())
    assert H2.number_of_modules() < 7
    assert H2.number_of_nets() == 2
    assert H2.number_of_pins() < 13
    assert H2.get_max_degree() <= 3
    assert H2.get_max_net_degree() <= 3
    assert not H.has_fixed_modules
    assert H.get_module_weight(1) == 3


if __name__ == "__main__":
    test_min_net_cover_pd()
