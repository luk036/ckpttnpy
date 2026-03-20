"""Mock classes for testing ckpttnpy modules.

This module provides mock implementations of hypergraph and graph classes
for unit testing purposes. These mocks simulate the interface of the
actual Netlist and related classes without requiring external dependencies.
"""

from typing import Any, Dict, List, Union

Part = Union[Dict[Any, int], List[int]]


class MockUgraph:
    """Mock bipartite graph for testing hypergraph operations.

    This class simulates the underlying bipartite graph structure used
    in hypergraph representations. It provides a simplified interface
    for accessing node degrees and neighbor lists.
    """

    def __init__(self):
        """Initialize the mock graph with sample data.

        Creates a mock bipartite graph with sample nets and modules
        for testing purposes.
        """
        self.degree = {"n1": 2, "n2": 3, "n3": 4}
        self.graph = {"n1": [0, 1], "n2": [0, 1, 2], "n3": [0, 1, 2, 3]}

    def __getitem__(self, key):
        """Get the neighbor list for a given node.

        Args:
            key: The node identifier (net name)

        Returns:
            List of module indices connected to the specified net
        """
        return self.graph[key]


class MockHyprgraph:
    """Mock hypergraph for testing partitioning algorithms.

    This class provides a simplified mock implementation of a hypergraph
    (netlist) for unit testing. It simulates the essential interface
    required by the gain calculation and partitioning managers.
    """

    def __init__(self):
        """Initialize the mock hypergraph with sample data.

        Creates a mock hypergraph with 4 modules and 3 nets
        for testing purposes.
        """
        self.modules = range(4)
        self.nets = ["n1", "n2", "n3"]
        self.ugraph = MockUgraph()
        self.net_weights = {"n1": 2, "n2": 3, "n3": 4}

    def __iter__(self):
        """Iterate over modules in the hypergraph.

        Returns:
            Iterator over module indices
        """
        return iter(self.modules)

    def get_net_weight(self, net):
        """Get the weight of a specified net.

        Args:
            net: The net identifier

        Returns:
            int: The weight of the specified net, defaults to 1
        """
        return self.net_weights[net]
