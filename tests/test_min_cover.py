from netlistx.netlist import create_drawf

from ckpttnpy.min_cover import (
    MINHASH_SIG_SIZE,
    MINHASH_SIMILARITY,
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


# if __name__ == "__main__":
#     test_min_net_cover_pd()
