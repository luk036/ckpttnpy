from ckpttnpy.min_cover import contract_subgraph
from ckpttnpy.netlist import create_drawf

# def test_max_independent_net():
#     # random_graph(gra,5,20)
#     hgr = create_drawf()
#     _, cost1 = max_independent_net(hgr, hgr.module_weight, set())
#     assert cost1 == 3


def test_contract_subgraph():
    hgr = create_drawf()
    hgr2, module_weight2 = contract_subgraph(hgr, hgr.module_weight, set())
    contract_subgraph(hgr2, module_weight2, set())
    assert hgr2.number_of_modules() < 7
    assert hgr2.number_of_nets() == 1
    assert hgr2.number_of_pins() < 13
    assert hgr2.get_max_degree() <= 3
    # assert hgr2.get_max_net_degree() <= 3
    # assert not hgr.has_fixed_modules
    assert hgr.get_module_weight("a1") == 3


# if __name__ == "__main__":
#     test_min_net_cover_pd()
