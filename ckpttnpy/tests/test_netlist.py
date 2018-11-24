import networkx as nx
from ckpttnpy.netlist import Netlist


def create_drawf():
    G = nx.Graph()
    cell_name = ['a0', 'a1', 'a2', 'a3', 'p1', 'p2', 'p3']
    G.add_nodes_from([
        (0, {'weight': 1}),
        (1, {'weight': 3}),
        (2, {'weight': 4}),
        (3, {'weight': 2}),
        (4, {'weight': 0}),
        (5, {'weight': 0}),
        (6, {'weight': 0}),
        (7, {'weight': 1}),
        (8, {'weight': 1}),
        (9, {'weight': 1}),
        (10, {'weight': 1}),
        (11, {'weight': 1})
    ])
    cell_list = [0, 1, 2, 3, 4, 5, 6]
    # cell_fixed = {}
    cell_weight = [1, 3, 4, 2, 0, 0, 0]
    net_list = [7, 8, 9, 10, 11]
    net_weight = [1, 1, 1, 1, 1]

    G.add_edges_from([
        (4, 7, {'dir': 'O'}),
        (0, 7, {'dir': 'I'}),
        (1, 7, {'dir': 'I'}),
        (0, 8, {'dir': 'O'}),
        (2, 8, {'dir': 'I'}),
        (3, 8, {'dir': 'I'}),
        (1, 9, {'dir': 'O'}),
        (2, 9, {'dir': 'I'}),
        (3, 9, {'dir': 'I'}),
        (2, 10, {'dir': 'O'}),
        (5, 10, {'dir': 'I'}),
        (3, 11, {'dir': 'O'}),
        (6, 11, {'dir': 'I'})
    ])

    H = Netlist(G, cell_list, net_list)
    H.cell_weight = cell_weight
    H.net_weight = net_weight
    H.cell_name = cell_name
    return H


def create_test_netlist():
    G = nx.Graph()
    G.add_nodes_from([
        (0, {'type': 'cell', 'weight': 5844}),
        (1, {'type': 'cell', 'weight': 5456, 'ispad': True}),
        (2, {'type': 'cell', 'weight': 5345}),
        (3, {'type': 'net', 'weight': 1}),
        (4, {'type': 'net', 'weight': 1}),
        (5, {'type': 'net', 'weight': 1})
    ])
    cell_list = [0, 1, 2]
    # cell_fixed = {}
    cell_weight = [533, 543, 532]
    net_list = [3, 4, 5]
    net_weight = [1, 1, 1]

    G.add_edges_from([
        (0, 3, {'dir': 'in'}),
        (0, 4, {'dir': 'out'}),
        (1, 3, {'dir': 'bidir'}),
        (1, 4, {'dir': 'unknown'}),
        (2, 4, {'dir': 'unknown'}),
        (0, 5, {'dir': 'bidir'})  # self-loop
    ])

    H = Netlist(G, cell_list, net_list)
    H.cell_weight = cell_weight
    H.net_weight = net_weight
    return H


# G = nx.DiGraph(G)

def test_netlist():
    H = create_test_netlist()
    assert H.number_of_cells() == 3
    assert H.number_of_nets() == 3
    assert H.number_of_pins() == 6
    assert H.get_max_degree() == 3
    assert H.get_max_net_degree() == 3
    assert not H.has_fixed_cells
    assert H.G.nodes[0].get('weight', 1) == 5844


def test_drawf():
    H = create_drawf()
    assert H.number_of_cells() == 7
    assert H.number_of_nets() == 5
    assert H.number_of_pins() == 13
    assert H.get_max_degree() == 3
    assert H.get_max_net_degree() == 3
    assert not H.has_fixed_cells
    assert H.G.nodes[1].get('weight', 1) == 3
