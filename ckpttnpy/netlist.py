import networkx as nx


class Netlist:
    G = nx.DiGraph()
    cell_list = []
    net_list = []
    cell_dict = {}
    vertex_list = []
    cell_fixed = {}

    has_fixed_cells = False
    max_degree = 0
    cost_model = 0

    def __init__(self):
        self.max_degree = max(self.G.out_degree[cell]
                              for cell in self.cell_list)

    def number_of_cells(self):
        return len(self.cell_list)

    def number_of_nets(self):
        return len(self.net_list)

    def number_of_pins(self):
        return self.G.number_of_edges() / 2

    def get_max_degree(self):
        return self.max_degree
