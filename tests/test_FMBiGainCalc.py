from typing import Any

import pytest
from ckpttnpy.FMBiGainCalc import FMBiGainCalc
from tests.mocks import MockHyprgraph


@pytest.fixture
def hyprgraph() -> Any:
    return MockHyprgraph()


@pytest.fixture
def gain_calc(hyprgraph: Any) -> Any:
    return FMBiGainCalc(hyprgraph)


@pytest.mark.parametrize(
    "net, part, totalcost, expected_gains",
    [
        ("n1", [0, 0, 0, 0], 0, {0: -2, 1: -2}),
        ("n1", [0, 1, 0, 0], 2, {0: 2, 1: 2}),
        ("n2", [0, 0, 0, 0], 0, {0: -3, 1: -3, 2: -3}),
        ("n2", [0, 0, 1, 0], 3, {0: 0, 1: 0, 2: 3}),
        ("n3", [0, 0, 0, 0], 0, {0: -4, 1: -4, 2: -4, 3: -4}),
        ("n3", [0, 0, 1, 1], 4, {0: 0, 1: 0, 2: 0, 3: 0}),
    ],
)
def test_init_gain(gain_calc: Any, hyprgraph: Any, net: Any, part: Any, totalcost: Any, expected_gains: Any) -> None:
    hyprgraph.nets = [net]
    gain_calc.init(part)
    assert gain_calc.totalcost == totalcost
    for v, gain in expected_gains.items():
        assert gain_calc.vertex_list[v].data[0] == gain
