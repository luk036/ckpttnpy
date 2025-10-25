import pytest
from ckpttnpy.FMBiGainCalc import FMBiGainCalc


class MockUgraph:
    def __init__(self):
        self.degree = {"n1": 2, "n2": 3, "n3": 4}
        self.graph = {"n1": [0, 1], "n2": [0, 1, 2], "n3": [0, 1, 2, 3]}

    def __getitem__(self, key):
        return self.graph[key]


class MockHyprgraph:
    def __init__(self):
        self.modules = range(4)
        self.nets = ["n1", "n2", "n3"]
        self.ugraph = MockUgraph()
        self.net_weights = {"n1": 2, "n2": 3, "n3": 4}

    def __iter__(self):
        return iter(self.modules)

    def get_net_weight(self, net):
        return self.net_weights[net]


@pytest.fixture
def hyprgraph():
    return MockHyprgraph()


@pytest.fixture
def gain_calc(hyprgraph):
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
def test_init_gain(gain_calc, hyprgraph, net, part, totalcost, expected_gains):
    hyprgraph.nets = [net]
    gain_calc.init(part)
    assert gain_calc.totalcost == totalcost
    for v, gain in expected_gains.items():
        assert gain_calc.vertex_list[v].data[0] == gain
