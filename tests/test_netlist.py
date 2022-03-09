import json

from networkx.readwrite import json_graph

from ckpttnpy.netlist import create_drawf, create_test_netlist, read_json


def test_netlist():
    hgr = create_test_netlist()
    assert hgr.number_of_modules() == 3
    assert hgr.number_of_nets() == 3
    assert hgr.number_of_nodes() == 6
    assert hgr.number_of_pins() == 6
    assert hgr.get_max_degree() == 3
    # assert hgr.get_max_net_degree() == 3
    # assert not hgr.has_fixed_modules
    # assert hgr.get_module_weight_by_id(0) == 533
    assert isinstance(hgr.module_weight, dict)


def test_drawf():
    hgr = create_drawf()
    assert hgr.number_of_modules() == 7
    assert hgr.number_of_nets() == 6
    assert hgr.number_of_pins() == 14
    assert hgr.get_max_degree() == 3
    # assert hgr.get_max_net_degree() == 3
    # assert not hgr.has_fixed_modules
    # assert hgr.get_module_weight_by_id(1) == 3


def test_json():
    # hgr = create_drawf()
    # data = json_graph.node_link_data(hgr.gr)
    # with open('testcases/drawf.json', 'w') as fw:
    #     json.dump(data, fw, indent=1)
    with open("testcases/drawf.json", "r") as fr:
        data2 = json.load(fr)
    gr = json_graph.node_link_graph(data2)
    assert gr.number_of_nodes() == 13
    assert gr.graph["num_modules"] == 7
    assert gr.graph["num_nets"] == 6
    assert gr.graph["num_pads"] == 3


def test_json2():
    with open("testcases/p1.json", "r") as fr:
        data = json.load(fr)
    gr = json_graph.node_link_graph(data)
    assert gr.number_of_nodes() == 1735
    assert gr.graph["num_modules"] == 833
    assert gr.graph["num_nets"] == 902
    assert gr.graph["num_pads"] == 81


def test_readjson():
    hgr = read_json("testcases/p1.json")
    count_2 = 0
    count_3 = 0
    count_rest = 0
    for net in hgr.nets:
        deg = hgr.gr.degree(net)
        if deg == 2:
            count_2 += 1
        elif deg == 3:
            count_3 += 1
        else:
            count_rest += 1
    print(count_2, count_3, count_rest)
    assert count_2 == 494
