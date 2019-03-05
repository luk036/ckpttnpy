import networkx as nx
from ckpttnpy.netlist import Netlist, ThinGraph
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
                range(num_modules), range(-num_modules, num_nets))
    H.num_pads = num_pads
    return H


def create_drawf():
    G = ThinGraph()
    G.add_nodes_from([
        'a0',
        'a1',
        'a2',
        'a3',
        'p1',
        'p2',
        'p3',
        'n0',
        'n1',
        'n2',
        'n3',
        'n4',
        'n5',
    ])
    nets = [
        'n0',
        'n1',
        'n2',
        'n3',
        'n4',
        'n5',
    ]
    net_map = {net : i_net for i_net, net in enumerate(nets)}
    modules = [
        'a0',
        'a1',
        'a2',
        'a3',
        'p1',
        'p2',
        'p3'
    ]
    module_map = {v : i_v for i_v, v in enumerate(modules)}
    module_weight = [1, 3, 4, 2, 0, 0, 0]

    G.add_edges_from([
        ('n0', 'p1', {'dir': 'I'}),
        ('n0', 'a0', {'dir': 'I'}),
        ('n0', 'a1', {'dir': 'O'}),
        ('n1', 'a0', {'dir': 'I'}),
        ('n1', 'a2', {'dir': 'I'}),
        ('n1', 'a3', {'dir': 'O'}),
        ('n2', 'a1', {'dir': 'I'}),
        ('n2', 'a2', {'dir': 'I'}),
        ('n2', 'a3', {'dir': 'O'}),
        ('n3', 'a2', {'dir': 'I'}),
        ('n3', 'p2', {'dir': 'O'}),
        ('n4', 'a3', {'dir': 'I'}),
        ('n4', 'p3', {'dir': 'O'}),
        ('n5', 'p2', {'dir': 'B'})
    ])
    G.graph['num_modules'] = 7
    G.graph['num_nets'] = 6
    G.graph['num_pads'] = 3
    # H = Netlist(G, range(7), range(7, 13), range(7), range(-7, 6))
    H = Netlist(G, modules, nets, module_map, net_map)
    H.module_weight = module_weight
    # H.module_name = module_name
    # H.net_weight = [1, 1, 1, 1, 1, 1]
    H.num_pads = 3
    return H


def create_test_netlist():
    G = ThinGraph()
    G.add_nodes_from([
        'a0',
        'a1',
        'a2',
        'a3',
        'a4',
        'a5'
    ])
    # module_list = [0, 1, 2]
    # module_fixed = {}
    module_weight = [533, 543, 532]
    # net_list = [3, 4, 5]

    G.add_edges_from([
        ('a3', 'a0'),
        ('a3', 'a1'),
        ('a4', 'a0'),
        ('a4', 'a1'),
        ('a4', 'a2'),
        ('a5', 'a0')  # self-loop
    ])

    G.graph['num_modules'] = 3
    G.graph['num_nets'] = 3
    modules = [
        'a0',
        'a1',
        'a2'
    ]
    module_map = {v : i_v for i_v, v in enumerate(modules)}
    nets = [
        'a3',
        'a4',
        'a5'
    ]
    net_map = {net : i_net for i_net, net in enumerate(nets)}

    # H = Netlist(G, range(3), range(3, 6), range(3), range(-3, 3))
    H = Netlist(G, modules, nets, module_map, net_map)
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
    assert H.get_module_weight_by_id(0) == 533


def test_drawf():
    H = create_drawf()

    assert H.number_of_modules() == 7
    assert H.number_of_nets() == 6
    assert H.number_of_pins() == 14
    assert H.get_max_degree() == 3
    assert H.get_max_net_degree() == 3
    assert not H.has_fixed_modules
    assert H.get_module_weight_by_id(1) == 3

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
