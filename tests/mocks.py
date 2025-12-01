from typing import Any, Dict, Iterator, List, Union

Part = Union[Dict[Any, int], List[int]]


class MockUgraph:
    def __init__(self) -> None:
        self.degree = {"n1": 2, "n2": 3, "n3": 4}
        self.graph = {"n1": [0, 1], "n2": [0, 1, 2], "n3": [0, 1, 2, 3]}

    def __getitem__(self, key: Any) -> Any:
        return self.graph[key]


class MockHyprgraph:
    def __init__(self) -> None:
        self.modules = range(4)
        self.nets = ["n1", "n2", "n3"]
        self.ugraph = MockUgraph()
        self.net_weights = {"n1": 2, "n2": 3, "n3": 4}

    def __iter__(self) -> Iterator:
        return iter(self.modules)

    def get_net_weight(self, net: Any) -> Any:
        return self.net_weights[net]
