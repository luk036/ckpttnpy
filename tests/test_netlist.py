
import json

from networkx.readwrite import json_graph

from ckpttnpy.netlist import create_drawf, create_test_netlist, read_json


def test_netlist():
    H = create_test_netlist()
    assert H.number_of_modules() == 3
    assert H.number_of_nets() == 3
    assert H.number_of_nodes() == 6
    assert H.number_of_pins() == 6
    assert H.get_max_degree() == 3
    # assert H.get_max_net_degree() == 3
    # assert not H.has_fixed_modules
    # assert H.get_module_weight_by_id(0) == 533
    assert isinstance(H.module_weight, dict)


def test_drawf():
    H = create_drawf()
    assert H.number_of_modules() == 7
    assert H.number_of_nets() == 6
    assert H.number_of_pins() == 14
    assert H.get_max_degree() == 3
    # assert H.get_max_net_degree() == 3
    # assert not H.has_fixed_modules
    # assert H.get_module_weight_by_id(1) == 3


def test_json():
    # H = create_drawf()
    # data = json_graph.node_link_data(H.G)
    # with open('testcases/drawf.json', 'w') as fw:
    #     json.dump(data, fw, indent=1)
    with open('testcases/drawf.json', 'r') as fr:
        data2 = json.load(fr)
    G = json_graph.node_link_graph(data2)
    assert G.number_of_nodes() == 13
    assert G.graph['num_modules'] == 7
    assert G.graph['num_nets'] == 6
    assert G.graph['num_pads'] == 3


def test_json2():
    with open('testcases/p1.json', 'r') as fr:
        data = json.load(fr)
    G = json_graph.node_link_graph(data)
    assert G.number_of_nodes() == 1735
    assert G.graph['num_modules'] == 833
    assert G.graph['num_nets'] == 902
    assert G.graph['num_pads'] == 81


def test_readjson():
    H = read_json('testcases/p1.json')
    count_2 = 0
    count_3 = 0
    count_rest = 0
    for net in H.nets:
        deg = H.G.degree(net)
        if deg == 2:
            count_2 += 1
        elif deg == 3:
            count_3 += 1
        else:
            count_rest += 1
    print(count_2, count_3, count_rest)
    assert count_2 == 494
