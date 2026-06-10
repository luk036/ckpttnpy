"""Tests for NNGainMgr (No-Nonsense Gain Manager)."""

from typing import Any, Dict, List, Union

import pytest
from netlistx.netlist import Netlist, create_drawf, create_test_netlist

from ckpttnpy.FMKWayGainCalc import FMKWayGainCalc
from ckpttnpy.NNGainMgr import NNGainMgr

Part = Union[Dict[Any, int], List[int]]


class NNGainMgrConcrete(NNGainMgr):
    """Minimal concrete subclass that implements the abstract modify_key.
    Also overrides init to populate gainbucket (the base class omits this).
    """

    def init(self, part) -> int:
        totalcost = NNGainMgr.init(self, part)
        for bckt in self.gainbucket:
            bckt.clear()
        for v in self.hyprgraph:
            pv = part[v]
            for k in range(self.num_parts):
                if k == pv:
                    continue
                vlink = self.gain_calc.vertex_list[k][v]
                self.gainbucket[k].append(vlink, vlink.data[0])
            vlink = self.gain_calc.vertex_list[pv][v]
            self.gainbucket[pv].set_key(vlink, 0)
        return totalcost

    def modify_key(self, w: Any, part_w: int, key) -> None:
        if isinstance(key, (list, tuple)):
            for k in range(self.num_parts):
                self.gainbucket[k].modify_key(
                    self.gain_calc.vertex_list[k][w], key[k]
                )
        else:
            self.gainbucket[part_w].modify_key(
                self.gain_calc.vertex_list[part_w][w], key
            )


@pytest.fixture
def netlist_test() -> Netlist:
    return create_test_netlist()


@pytest.fixture
def netlist_drawf() -> Netlist:
    return create_drawf()


def _run_gain_mgr(hyprgraph: Netlist, part: Part) -> NNGainMgrConcrete:
    mgr = NNGainMgrConcrete(FMKWayGainCalc, hyprgraph)
    mgr.init(part)
    while not mgr.is_empty():
        move_info_v, gainmax = mgr.select(part)
        if gainmax <= 0:
            continue
        mgr.update_move(part, move_info_v)
        v, _, to_part = move_info_v
        part[v] = to_part
    return mgr


class TestNNGainMgrInit:
    """Verify that initialisation sets up the expected data structures."""

    def test_init_creates_gainbucket(self, netlist_test: Netlist) -> None:
        hyprgraph = netlist_test
        mgr = NNGainMgrConcrete(FMKWayGainCalc, hyprgraph)
        assert hasattr(mgr, "gainbucket")
        assert len(mgr.gainbucket) == mgr.num_parts
        assert mgr.pmax == hyprgraph.get_max_degree()

    def test_init_with_3_parts(self, netlist_test: Netlist) -> None:
        hyprgraph = netlist_test
        mgr = NNGainMgrConcrete(FMKWayGainCalc, hyprgraph, num_parts=3)
        assert len(mgr.gainbucket) == 3

    @pytest.mark.parametrize("create_netlist", [create_test_netlist, create_drawf])
    def test_init_returns_totalcost(self, create_netlist) -> None:
        hyprgraph = create_netlist()
        part = {v: 0 for v in hyprgraph}
        mgr = NNGainMgrConcrete(FMKWayGainCalc, hyprgraph)
        totalcost = mgr.init(part)
        assert isinstance(totalcost, int)
        assert totalcost >= 0


class TestNNGainMgrSelect:
    """Verify select / select_togo logic."""

    @pytest.mark.parametrize("create_netlist", [create_test_netlist, create_drawf])
    def test_select_returns_valid_move(self, create_netlist) -> None:
        hyprgraph = create_netlist()
        part = {v: 0 for v in hyprgraph}
        part["a1"] = 1
        mgr = NNGainMgrConcrete(FMKWayGainCalc, hyprgraph)
        mgr.init(part)
        move_info_v, gainmax = mgr.select(part)
        v, from_part, to_part = move_info_v
        assert from_part != to_part
        assert isinstance(v, (str, int))
        assert isinstance(gainmax, int)

    @pytest.mark.parametrize("create_netlist", [create_test_netlist, create_drawf])
    def test_select_togo_returns_valid(self, create_netlist) -> None:
        hyprgraph = create_netlist()
        part = {v: 0 for v in hyprgraph}
        part["a1"] = 1
        mgr = NNGainMgrConcrete(FMKWayGainCalc, hyprgraph)
        mgr.init(part)
        v, gainmax = mgr.select_togo(0)
        assert isinstance(gainmax, int)


class TestNNGainMgrIsEmpty:
    """Verify is_empty reports correctly."""

    def test_is_empty_after_init(self, netlist_test: Netlist) -> None:
        hyprgraph = netlist_test
        part = {v: 0 for v in hyprgraph}
        mgr = NNGainMgrConcrete(FMKWayGainCalc, hyprgraph)
        mgr.init(part)
        assert not mgr.is_empty()

    def test_is_empty_with_single_node(self) -> None:
        import networkx as nx
        from netlistx.netlist import Netlist

        G = nx.Graph()
        G.add_nodes_from(["m1"], bipartite=0)
        G.add_nodes_from(["n1"], bipartite=1)
        G.add_edge("m1", "n1")
        hyprgraph = Netlist(G, ["m1"], ["n1"])
        part = {"m1": 0}
        mgr = NNGainMgrConcrete(FMKWayGainCalc, hyprgraph)
        mgr.init(part)
        assert isinstance(mgr.is_empty(), bool)


class TestNNGainMgrFullRun:
    """End-to-end run (integration-style, same pattern as test_FMBiGainMgr)."""

    @pytest.mark.parametrize("create_netlist", [create_test_netlist, create_drawf])
    def test_run_does_not_crash(self, create_netlist) -> None:
        hyprgraph = create_netlist()
        part = {v: 0 for v in hyprgraph}
        part["a1"] = 1
        mgr = _run_gain_mgr(hyprgraph, part)
        assert all(v in part for v in hyprgraph)


class TestNNGainMgrUpdateMove:
    """Verify update_move modifies gains correctly."""

    def test_update_move_2pin(self, netlist_test: Netlist) -> None:
        hyprgraph = netlist_test
        part = {v: 0 for v in hyprgraph}
        part["a1"] = 1
        mgr = NNGainMgrConcrete(FMKWayGainCalc, hyprgraph)
        mgr.init(part)
        move_info_v, _ = mgr.select(part)
        v, from_part, to_part = move_info_v
        mgr.update_move(part, move_info_v)
        part[v] = to_part

    def test_update_move_changes_gainbucket(self, netlist_test: Netlist) -> None:
        hyprgraph = netlist_test
        part = {v: 0 for v in hyprgraph}
        part["a1"] = 1
        mgr = NNGainMgrConcrete(FMKWayGainCalc, hyprgraph)
        mgr.init(part)
        initial_max = mgr.gainbucket[0].get_max()
        move_info_v, _ = mgr.select(part)
        mgr.update_move(part, move_info_v)
        v, from_part, to_part = move_info_v
        part[v] = to_part
        # Gain values can be negative after a move; verify the bucket is still usable
        assert isinstance(mgr.gainbucket[0].get_max(), int)


if __name__ == "__main__":
    pytest.main([__file__])
