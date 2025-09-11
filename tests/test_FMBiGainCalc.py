import unittest

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


class TestFMBiGainCalc(unittest.TestCase):
    def setUp(self):
        self.hyprgraph = MockHyprgraph()
        self.gain_calc = FMBiGainCalc(self.hyprgraph)

    def test_init_gain_2pin_net(self):
        part = [0, 0, 0, 0]
        self.hyprgraph.nets = ["n1"]
        self.gain_calc.init(part)
        self.assertEqual(self.gain_calc.totalcost, 0)
        self.assertEqual(self.gain_calc.vertex_list[0].data[0], -2)
        self.assertEqual(self.gain_calc.vertex_list[1].data[0], -2)

        part = [0, 1, 0, 0]
        self.gain_calc.init(part)
        self.assertEqual(self.gain_calc.totalcost, 2)
        self.assertEqual(self.gain_calc.vertex_list[0].data[0], 2)
        self.assertEqual(self.gain_calc.vertex_list[1].data[0], 2)

    def test_init_gain_3pin_net(self):
        part = [0, 0, 0, 0]
        self.hyprgraph.nets = ["n2"]
        self.gain_calc.init(part)
        self.assertEqual(self.gain_calc.totalcost, 0)
        self.assertEqual(self.gain_calc.vertex_list[0].data[0], -3)
        self.assertEqual(self.gain_calc.vertex_list[1].data[0], -3)
        self.assertEqual(self.gain_calc.vertex_list[2].data[0], -3)

        part = [0, 0, 1, 0]
        self.gain_calc.init(part)
        self.assertEqual(self.gain_calc.totalcost, 3)
        self.assertEqual(self.gain_calc.vertex_list[0].data[0], 0)
        self.assertEqual(self.gain_calc.vertex_list[1].data[0], 0)
        self.assertEqual(self.gain_calc.vertex_list[2].data[0], 3)

    def test_init_gain_general_net(self):
        part = [0, 0, 0, 0]
        self.hyprgraph.nets = ["n3"]
        self.gain_calc.init(part)
        self.assertEqual(self.gain_calc.totalcost, 0)
        self.assertEqual(self.gain_calc.vertex_list[0].data[0], -4)
        self.assertEqual(self.gain_calc.vertex_list[1].data[0], -4)
        self.assertEqual(self.gain_calc.vertex_list[2].data[0], -4)
        self.assertEqual(self.gain_calc.vertex_list[3].data[0], -4)

        part = [0, 0, 1, 1]
        self.gain_calc.init(part)
        self.assertEqual(self.gain_calc.totalcost, 4)
        self.assertEqual(self.gain_calc.vertex_list[0].data[0], 0)
        self.assertEqual(self.gain_calc.vertex_list[1].data[0], 0)
        self.assertEqual(self.gain_calc.vertex_list[2].data[0], 0)
        self.assertEqual(self.gain_calc.vertex_list[3].data[0], 0)


if __name__ == "__main__":
    unittest.main()
