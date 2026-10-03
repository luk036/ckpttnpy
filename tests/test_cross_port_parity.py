"""Cross-port parity checks against the C++ and Rust ports.

The three ports must agree on the constants that define shared algebraic
behaviour: the FM net-degree cap and the MinHash duplicate-detection
parameters. Each sibling is located next to this checkout (or via the
``CKPTTN_CPP_DIR`` / ``CKPTTN_RS_DIR`` environment variables); the per-port
tests are skipped when the corresponding checkout is absent, for example in CI
that clones a single repository.
"""

import os
import re
from pathlib import Path
from typing import Dict, Optional, Union

import pytest

from ckpttnpy import FMPmrConfig, min_cover


def _first_with(candidates, marker: str) -> Optional[Path]:
    for cand in candidates:
        if (cand / marker).is_file():
            return cand.resolve()
    return None


def _find_cpp_repo() -> Optional[Path]:
    candidates = []
    env = os.environ.get("CKPTTN_CPP_DIR")
    if env:
        candidates.append(Path(env))
    root = Path(__file__).resolve().parents[1]
    for base in (root.parent, root.parent.parent):
        candidates.append(base / "cpp" / "ckpttn-cpp")
        candidates.append(base / "ckpttn-cpp")
    return _first_with(candidates, "include/ckpttn/FMPmrConfig.hpp")


def _find_rs_repo() -> Optional[Path]:
    candidates = []
    env = os.environ.get("CKPTTN_RS_DIR")
    if env:
        candidates.append(Path(env))
    root = Path(__file__).resolve().parents[1]
    for base in (root.parent, root.parent.parent):
        candidates.append(base / "rs" / "ckpttn-rs")
        candidates.append(base / "ckpttn-rs")
    return _first_with(candidates, "src/fm_pmr_config.rs")


CPP_REPO = _find_cpp_repo()
RS_REPO = _find_rs_repo()

skip_cpp = pytest.mark.skipif(
    CPP_REPO is None, reason="ckpttn-cpp checkout not available"
)
skip_rs = pytest.mark.skipif(RS_REPO is None, reason="ckpttn-rs checkout not available")

_CPP_CONST_RE = re.compile(r"\b([A-Z][A-Z0-9_]*)\s*=\s*([A-Za-z0-9_.]+)")
_RS_CONST_RE = re.compile(
    r"\b([A-Z][A-Z0-9_]*)\s*:\s*[A-Za-z0-9_]+\s*=\s*([A-Za-z0-9_.]+)"
)


def _constants(
    repo: Optional[Path], relative_path: str, regex: re.Pattern
) -> Dict[str, str]:
    assert repo is not None
    return dict(regex.findall((repo / relative_path).read_text(encoding="utf-8")))


def _value(constants: Dict[str, str], name: str) -> Union[int, float]:
    token = constants[name]
    literal = token.rstrip("uUlLfF")
    try:
        return float(literal) if "." in literal else int(literal)
    except ValueError:
        return _value(constants, token)


@skip_cpp
def test_fm_max_degree_matches_cpp() -> None:
    fm = _constants(CPP_REPO, "include/ckpttn/FMPmrConfig.hpp", _CPP_CONST_RE)
    assert FMPmrConfig.FM_MAX_DEGREE == _value(fm, "FM_MAX_DEGREE")


@skip_rs
def test_fm_max_degree_matches_rs() -> None:
    fm = _constants(RS_REPO, "src/fm_pmr_config.rs", _RS_CONST_RE)
    assert FMPmrConfig.FM_MAX_DEGREE == _value(fm, "FM_MAX_DEGREE")


@skip_cpp
def test_minhash_constants_match_cpp() -> None:
    mc = _constants(CPP_REPO, "source/min_cover.cpp", _CPP_CONST_RE)
    assert min_cover.MINHASH_SIG_SIZE == _value(mc, "MINHASH_SIG_SIZE")
    assert min_cover.MINHASH_SIMILARITY == _value(mc, "MINHASH_SIMILARITY")
    assert min_cover.MINHASH_MAX_DEGREE == _value(mc, "MINHASH_MAX_DEGREE")
    assert min_cover.LOW_PIN_NET_THRESHOLD == _value(mc, "LOW_PIN_NET_THRESHOLD")


@skip_rs
def test_minhash_constants_match_rs() -> None:
    mc = _constants(RS_REPO, "src/min_cover.rs", _RS_CONST_RE)
    assert min_cover.MINHASH_SIG_SIZE == _value(mc, "MINHASH_SIG_SIZE")
    assert min_cover.MINHASH_SIMILARITY == _value(mc, "MINHASH_SIMILARITY")
    assert min_cover.MINHASH_MAX_DEGREE == _value(mc, "MINHASH_MAX_DEGREE")
    assert min_cover.LOW_PIN_NET_THRESHOLD == _value(mc, "LOW_PIN_NET_THRESHOLD")
