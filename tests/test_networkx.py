import networkx as nx


def test_Graph():
    G = nx.Graph()
    G.add_nodes_from([
        0,
        1,
        2,
        3])
    G.add_edge(0, 1)
    G.add_edge(0, 1)
    assert G.number_of_edges() == 1


if __name__ == "__main__":
    test_Graph()
