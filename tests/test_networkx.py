import networkx as nx


def test_Graph():
    gr = nx.Graph()
    gr.add_nodes_from([0, 1, 2, 3])
    gr.add_edge(0, 1)
    gr.add_edge(0, 1)
    assert gr.number_of_edges() == 1


if __name__ == "__main__":
    test_Graph()
