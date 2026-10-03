import pytest
from netlistx.netlist import Netlist, create_drawf, create_test_netlist

from ckpttnpy.FMBiGainCalc import FMBiGainCalc
from ckpttnpy.FMBiGainMgr import FMBiGainMgr
from tests.mocks import Part


def _run_FMBiGainMgr(hyprgraph: Netlist, part: Part):
    mgr = FMBiGainMgr(FMBiGainCalc, hyprgraph)
    mgr.init(part)
    while not mgr.is_empty():
        # Take the gainmax with v from gainbucket
        move_info_v, gainmax = mgr.select(part)
        if gainmax <= 0:
            continue
        mgr.update_move(part, move_info_v)
        mgr.update_move_v(move_info_v, gainmax)
        v, _, to_part = move_info_v
        part[v] = to_part
        # assert v >= 0


@pytest.mark.parametrize("create_netlist", [create_test_netlist, create_drawf])
def test_FMBiGainMgr(create_netlist) -> None:
    hyprgraph = create_netlist()
    part = {v: 0 for v in hyprgraph}
    part["a1"] = 1
    _run_FMBiGainMgr(hyprgraph, part)


def test_fm_max_degree_excludes_large_nets() -> None:
    """Nets above FM_MAX_DEGREE are excluded from gain and cost accounting."""
    import networkx as nx

    from ckpttnpy.FMPmrConfig import FM_MAX_DEGREE

    num_modules = FM_MAX_DEGREE + 1
    huge_net = num_modules
    small_net = num_modules + 1
    graph = nx.Graph()
    modules = list(range(num_modules))
    graph.add_nodes_from(modules, bipartite=0)
    graph.add_nodes_from([huge_net, small_net], bipartite=1)
    graph.add_edges_from((huge_net, m) for m in modules)
    graph.add_edge(small_net, 0)
    graph.add_edge(small_net, 1)

    hyprgraph = Netlist(graph, modules, [huge_net, small_net])
    part = [0] * num_modules
    part[1] = 1

    mgr = FMBiGainMgr(FMBiGainCalc, hyprgraph)
    assert mgr.init(part) == 1
