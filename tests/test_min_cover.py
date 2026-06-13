from netlistx.netlist import create_drawf

from ckpttnpy.min_cover import (
    _jaccard_similarity,
    _minhash_signature,
    contract_subgraph,
)


def test_minhash_identical_sets() -> None:
    """Identical sets should have Jaccard similarity = 1.0."""
    items = list(range(100))
    sig1 = _minhash_signature(items)
    sig2 = _minhash_signature(items)
    sim = _jaccard_similarity(sig1, sig2)
    assert sim == 1.0


def test_minhash_disjoint_sets() -> None:
    """Disjoint sets should have Jaccard similarity near 0."""
    sig1 = _minhash_signature(range(0, 100))
    sig2 = _minhash_signature(range(200, 300))
    sim = _jaccard_similarity(sig1, sig2)
    assert sim < 0.05


def test_minhash_partial_overlap() -> None:
    """Partially overlapping sets should have intermediate similarity."""
    sig1 = _minhash_signature(range(100))
    sig2 = _minhash_signature(range(50, 150))  # 50% overlap
    sim = _jaccard_similarity(sig1, sig2)
    assert 0.3 < sim < 0.8


def test_minhash_empty_set() -> None:
    """Empty sets trivially match (both empty = same set)."""
    sig = _minhash_signature([])
    assert _jaccard_similarity(sig, sig) == 1.0

    # One empty, one non-empty
    sig2 = _minhash_signature([1, 2, 3])
    assert _jaccard_similarity(sig, sig2) == 0.0


def test_minhash_different_sizes() -> None:
    """Signatures of different sizes should not crash."""
    sig1 = _minhash_signature(range(100), k=64)
    sig2 = _minhash_signature(range(100), k=32)
    sim = _jaccard_similarity(sig1, sig2)
    assert sim == 1.0  # Same content, compared over min length


def test_minhash_signature_length() -> None:
    """Signature should have the requested length."""
    sig = _minhash_signature(range(50), k=128)
    assert len(sig) == 128
    assert all(isinstance(v, int) for v in sig)


def test_minhash_deterministic() -> None:
    """Same input should produce same signature."""
    sig1 = _minhash_signature([1, 2, 3, 4, 5])
    sig2 = _minhash_signature([1, 2, 3, 4, 5])
    assert sig1 == sig2


# def test_max_independent_net() -> None:
#     # random_graph(ugraph,5,20)
#     hyprgraph = create_drawf()
#     _, cost1 = max_independent_net(hyprgraph, hyprgraph.module_weight, set())
#     assert cost1 == 3


def test_contract_subgraph() -> None:
    hyprgraph = create_drawf()
    hgr2, module_weight2 = contract_subgraph(hyprgraph, hyprgraph.module_weight, set())
    contract_subgraph(hgr2, module_weight2, set())
    assert hgr2.number_of_modules() < 7
    assert hgr2.number_of_nets() == 1
    assert hgr2.number_of_pins() < 13
    assert hgr2.get_max_degree() <= 3
    # assert hgr2.get_max_net_degree() <= 3
    # assert not hyprgraph.has_fixed_modules
    assert hyprgraph.module_weight["a1"] == 3  # type: ignore[call-overload]  # Original module_weight is a dict


# ── Edge case: jaccard_similarity with empty inputs ───────────────


def test_jaccard_identical_sets() -> None:
    sig = _minhash_signature([1, 2, 3])
    assert _jaccard_similarity(sig, sig) == 1.0


def test_jaccard_one_empty() -> None:
    """_jaccard_similarity should return 0.0 when one signature is empty."""
    sig1: list = []
    sig2 = _minhash_signature([1, 2, 3])
    assert _jaccard_similarity(sig1, sig2) == 0.0


def test_jaccard_both_empty() -> None:
    """_jaccard_similarity should return 0.0 when both signatures are empty."""
    assert _jaccard_similarity([], []) == 0.0


# ── Contract subgraph with non-default net weights ────────────────


def test_contract_subgraph_with_weights() -> None:
    """Verify contract_subgraph handles nets with non-default weights."""
    import networkx as nx
    from netlistx.netlist import Netlist

    G = nx.Graph()
    modules = [0, 1, 2, 3]
    nets = [4, 5, 6]
    G.add_nodes_from(modules, bipartite=0)
    G.add_nodes_from(nets, bipartite=1)
    G.add_edges_from(
        [
            (4, 0),
            (4, 1),
            (4, 2),  # net 4 connects 3 modules
            (5, 1),
            (5, 3),  # net 5 connects 2 modules
            (6, 3),  # net 6 connects 1 module (self-loop after contract)
        ]
    )

    hyprgraph = Netlist(G, modules, nets)
    module_weight = [1, 1, 1, 1]

    hgr2, module_weight2 = contract_subgraph(hyprgraph, module_weight, set())
    # Should not crash and produce a smaller hypergraph
    assert hgr2.number_of_modules() < 4


# ── MinHash duplicate detection with high-pin nets ────────────────


def test_purge_duplicate_nets_minhash() -> None:
    """Exercise the minHash branch in purge_duplicate_nets (degree > 5 and <= 200)."""
    import networkx as nx
    from netlistx.netlist import Netlist

    from ckpttnpy.min_cover import (
        LOW_PIN_NET_THRESHOLD,
        construct_graph,
        purge_duplicate_nets,
        setup,
    )

    num_cells = LOW_PIN_NET_THRESHOLD + 2  # 7 cells to exceed low-pin threshold
    G = nx.Graph()
    modules = list(range(num_cells))
    nets = [num_cells, num_cells + 1]  # two nets
    G.add_nodes_from(modules, bipartite=0)
    G.add_nodes_from(nets, bipartite=1)
    for net in nets:
        for cell in modules:
            G.add_edge(net, cell)

    hyprgraph = Netlist(G, modules, nets)
    cluster_weight = {net: 1 for net in hyprgraph.nets}
    clusters, remaining_nets, cell_list = setup(hyprgraph, cluster_weight, set())
    ugraph = construct_graph(hyprgraph, remaining_nets, cell_list, clusters)
    num_modules = len(cell_list) + len(clusters)
    num_clusters = len(clusters)

    net_weight, updated_nets = purge_duplicate_nets(
        hyprgraph, ugraph, remaining_nets, num_clusters, num_modules
    )
    # Should not crash
    assert isinstance(net_weight, dict)
    assert isinstance(updated_nets, list)
