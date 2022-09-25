import networkx as nx


class Lict:
    def __init__(self, lst):
        self.rng = range(len(lst))
        self.lst = lst

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

    def values(self):
        return iter(self.lst)


# NUM_NODES = 1000


class TinyDiGraph(nx.DiGraph):
    num_nodes = 0

    def cheat_node_dict(self):
        return Lict([dict() for _ in range(self.num_nodes)])

    def cheat_adjlist_outer_dict(self):
        return Lict([dict() for _ in range(self.num_nodes)])

    node_dict_factory = cheat_node_dict
    adjlist_outer_dict_factory = cheat_adjlist_outer_dict

    def init_nodes(self, n: int):
        self.num_nodes = n
        self._node = self.cheat_node_dict()
        self._adj = self.cheat_adjlist_outer_dict()
        self._pred = self.cheat_adjlist_outer_dict()


if __name__ == "__main__":
    gr = TinyDiGraph()
    gr.init_nodes(1000)
    gr.add_edge(2, 1)
    print(gr.number_of_nodes())
    print(gr.number_of_edges())

    for u in gr:
        for v in gr.neighbors(u):
            print(f"{u}, {v}")

    a = Lict([0] * 8)
    for i in a:
        a[i] = i * i
    for i, v in a.items():
        print(f'{i}: {v}')
    print(3 in a)
