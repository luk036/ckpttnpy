import networkx as nx
from ckpttnpy.netlist import Netlist
from networkx.readwrite import json_graph
import json


def create_p1():
    with open('testcases/p1.json', 'r') as fr:
        data = json.load(fr)
    G = json_graph.node_link_graph(data)
    num_modules = G.graph['num_modules']
    num_nets = G.graph['num_nets']
    num_pads = G.graph['num_pads']
    H = Netlist(G, range(num_modules), range(num_modules, num_modules + num_nets),
                range(-num_modules, num_nets))
    H.num_pads = num_pads
    return H


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
        11,
        12
    ])
    # module_list = [0, 1, 2, 3, 4, 5, 6]
    # module_fixed = {}
    module_weight = [1, 3, 4, 2, 0, 0, 0]
    # net_list = [7, 8, 9, 10, 11]

    G.add_edges_from([
        (7, 4, {'dir': 'I'}),
        (7, 0, {'dir': 'I'}),
        (7, 1, {'dir': 'O'}),
        (8, 0, {'dir': 'I'}),
        (8, 2, {'dir': 'I'}),
        (8, 3, {'dir': 'O'}),
        (9, 1, {'dir': 'I'}),
        (9, 2, {'dir': 'I'}),
        (9, 3, {'dir': 'O'}),
        (10, 2, {'dir': 'I'}),
        (10, 5, {'dir': 'O'}),
        (11, 3, {'dir': 'I'}),
        (11, 6, {'dir': 'O'}),
        (12, 5, {'dir': 'B'})
    ])
    G.graph['num_modules'] = 7
    G.graph['num_nets'] = 6
    G.graph['num_pads'] = 3
    H = Netlist(G, range(7), range(7, 13), range(-7, 6))
    H.module_weight = module_weight
    H.module_name = module_name
    # H.net_weight = [1, 1, 1, 1, 1, 1]
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
        (3, 0),
        (3, 1),
        (4, 0),
        (4, 1),
        (4, 2),
        (5, 0)  # self-loop
    ])

    G.graph['num_modules'] = 3
    G.graph['num_nets'] = 3
    H = Netlist(G, range(3), range(3, 6), range(-3, 3))
    H.module_weight = module_weight
    return H


# G = nx.DiGraph(G)

def test_netlist():
    H = create_test_netlist()
    assert H.number_of_modules() == 3
    assert H.number_of_nets() == 3
    assert H.number_of_nodes() == 6
    assert H.number_of_pins() == 6
    assert H.get_max_degree() == 3
    assert H.get_max_net_degree() == 3
    assert not H.has_fixed_modules
    assert H.get_module_weight(0) == 533


def test_drawf():
    H = create_drawf()

    assert H.number_of_modules() == 7
    assert H.number_of_nets() == 6
    assert H.number_of_pins() == 14
    assert H.get_max_degree() == 3
    assert H.get_max_net_degree() == 3
    assert not H.has_fixed_modules
    assert H.get_module_weight(1) == 3

    # nx.nx_agraph.write_dot(H.G, 'drawf.dot')


def test_json():
    from networkx.readwrite import json_graph
    import json
    H = create_drawf()
    data = json_graph.node_link_data(H.G)
    with open('testcases/drawf.json', 'w') as fw:
        json.dump(data, fw, indent=1)
    with open('testcases/drawf.json', 'r') as fr:
        data2 = json.load(fr)
    G = json_graph.node_link_graph(data2)
    assert G.number_of_nodes() == 13
    assert G.graph['num_modules'] == 7
    assert G.graph['num_nets'] == 6
    assert G.graph['num_pads'] == 3


def test_json2():
    from networkx.readwrite import json_graph
    import json
    with open('testcases/p1.json', 'r') as fr:
        data = json.load(fr)
    G = json_graph.node_link_graph(data)
    assert G.number_of_nodes() == 1735
    assert G.graph['num_modules'] == 833
    assert G.graph['num_nets'] == 902
    assert G.graph['num_pads'] == 81
