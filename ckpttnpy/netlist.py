import networkx as nx


class Netlist:
    cost_model = 0
    net_weight = []
    cell_weight = []

    def __init__(self, G, cell_list, net_list, cell_fixed={}):
        self.G = G
        self.cell_list = cell_list
        self.net_list = net_list
        self.cell_dict = {}

        for i_v, v in enumerate(self.cell_list):
            self.cell_dict[v] = i_v

        self.cell_fixed = cell_fixed
        self.has_fixed_cells = (self.cell_fixed != {})

        self.max_degree = max(self.G.degree[cell]
                              for cell in self.cell_list)
        self.max_net_degree = max(self.G.degree[net]
                              for net in self.net_list)

    def number_of_cells(self):
        return len(self.cell_list)

    def number_of_nets(self):
        return len(self.net_list)

    def number_of_pins(self):
        return self.G.number_of_edges()

    def get_max_degree(self):
        return self.max_degree

    def get_max_net_degree(self):
        return self.max_net_degree
