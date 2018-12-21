import networkx as nx
from ckpttnpy.netlist import Netlist


def create_drawf():
    G = nx.Graph()
    module_name = ['a0', 'a1', 'a2', 'a3', 'p1', 'p2', 'p3']
    G.add_nodes_from([
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11
    ])
    # module_list = [0, 1, 2, 3, 4, 5, 6]
    # module_fixed = {}
    module_weight = [1, 3, 4, 2, 0, 0, 0]
    # net_list = [7, 8, 9, 10, 11]

    G.add_edges_from([
        (4,  7),
        (0,  7),
        (1,  7),
        (0,  8),
        (2,  8),
        (3,  8),
        (1,  9),
        (2,  9),
        (3,  9),
        (2, 10),
        (5, 10),
        (3, 11),
        (6, 11)
    ])

    H = Netlist(G, range(7), range(7, 12), range(-7, 5))
    H.module_weight = module_weight
    H.module_name = module_name
    H.net_weight = [1, 1, 1, 1, 1]
    H.num_pads = 3
    return H


def create_test_netlist():
    G = nx.Graph()
    G.add_nodes_from([
        0,
        1,
        2,
        3,
        4,
        5
    ])
    # module_list = [0, 1, 2]
    # module_fixed = {}
    module_weight = [533, 543, 532]
    # net_list = [3, 4, 5]

    G.add_edges_from([
        (0, 3),
        (0, 4),
        (1, 3),
        (1, 4),
        (2, 4),
        (0, 5)  # self-loop
    ])

    H = Netlist(G, range(3), range(3, 6), range(-3, 3))
    H.module_weight = module_weight
    return H


# G = nx.DiGraph(G)

def test_netlist():
    H = create_test_netlist()
    assert H.number_of_modules() == 3
    assert H.number_of_nets() == 3
    assert H.number_of_pins() == 6
    assert H.get_max_degree() == 3
    assert H.get_max_net_degree() == 3
    assert not H.has_fixed_modules
    assert H.get_module_weight(0) == 533


def test_drawf():
    H = create_drawf()

    assert H.number_of_modules() == 7
    assert H.number_of_nets() == 5
    assert H.number_of_pins() == 13
    assert H.get_max_degree() == 3
    assert H.get_max_net_degree() == 3
    assert not H.has_fixed_modules
    assert H.get_module_weight(1) == 3

    # nx.nx_agraph.write_dot(H.G, 'drawf.dot')
