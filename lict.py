import networkx as nx


class Lict:
    def __init__(self, n, fn):
        self.rng = range(n)
        self.lst = [fn() for _ in self.rng]

    def items(self):
        return enumerate(self.lst)

    def __getitem__(self, key):
        return self.lst.__getitem__(key)

    def __setitem__(self, key, new_value):
        self.lst.__setitem__(key, new_value)

    def __iter__(self):
        return iter(self.rng)

    def __contains__(self, value):
        return value in self.rng

    def __len__(self):
        return len(self.rng)


NUM_NODES = 1000;


class TinyGraph(nx.Graph):
    all_edge_dict = {"weight": 1}
    all_node_dict = {"weight": 1}

    def single_edge_dict(self):
        return self.all_edge_dict
 
    def single_node_dict(self):
        return self.all_node_dict
 
    def trick_node_dict(self):
        return Lict(NUM_NODES, self.single_node_dict)

    def trick_adjlist_outer_dict(self):
        return Lict(NUM_NODES, dict)

    edge_attr_dict_factory = single_edge_dict
    node_attr_dict_factory = single_node_dict
    node_dict_factory = trick_node_dict
    adjlist_outer_dict_factory = trick_adjlist_outer_dict
    # adjlist_inner_dict_factory = dict
    # node_attr_dict_factory = dict


if __name__ == "__main__":
    gr = TinyGraph()
    gr.add_edge(2, 1)
    print(gr.number_of_nodes())
    print(gr.number_of_edges())

    for u in gr:
        for v in gr.neighbors(u):
            print(f"{u}, {v}")

    a = Lict(8, int)
    for i in a:
        a[i] = i * i
    for i, v in a.items():
        print(f'{i}: {v}')
    print(3 in a)
