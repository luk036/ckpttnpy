import networkx as nx
from ckpttnpy.netlist import Netlist


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


if __name__ == "__main__":
    test_netlist()
