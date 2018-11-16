import networkx as nx
from collections import deque
from ckpttnpy.dllist import dllink
from ckpttnpy.bpqueue import bpqueue
from ckpttnpy.netlist import Netlist

def create_test_netlist():
    G = nx.Graph()
    G.add_nodes_from([
        ('a1', {'type': 'cell', 'weight': 5844, 'fixed': True}),
        ('a2', {'type': 'cell', 'weight': 3456, 'ispad': True}),
        ('a3', {'type': 'cell', 'weight': 345}),
        ('n1', {'type': 'net', 'weight': 1}),
        ('n2', {'type': 'net', 'weight': 1}),
        ('n3', {'type': 'net', 'weight': 1})
    ])
    cell_list = ['a1', 'a2', 'a3']
    cell_fixed = {}
    cell_weight = [533, 343, 32]
    net_list = ['n1', 'n2', 'n3']
    net_weight = [1, 1, 1]

    G.add_edges_from([
        ('a1', 'n1', {'dir': 'in'}),
        ('a1', 'n2', {'dir': 'out'}),
        ('a2', 'n1', {'dir': 'bidir'}),
        ('a2', 'n2', {'dir': 'unknown'}),
        ('a3', 'n2', {'dir': 'unknown'}),
        ('a1', 'n3', {'dir': 'bidir'}) # self-loop
    ])

    H = Netlist(G, cell_list, net_list, cell_fixed)
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

if __name__ == "__main__":
    test_netlist()

