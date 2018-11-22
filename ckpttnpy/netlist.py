class Netlist:
    cost_model = 0
    net_weight = []
    cell_weight = []
    cell_fixed = {}

    def __init__(self, G, cell_list, net_list):
        """[summary]

        Arguments:
            G {[type]} -- [description]
            cell_list {[type]} -- [description]
            net_list {[type]} -- [description]

        Keyword Arguments:
            cell_fixed {dict} -- [description] (default: {{}})
        """
        self.G = G
        self.cell_list = cell_list
        self.net_list = net_list
        
        # self.cell_dict = {}
        # for i_v, v in enumerate(self.cell_list):
        #     self.cell_dict[v] = i_v

        # self.cell_fixed = cell_fixed
        self.has_fixed_cells = (self.cell_fixed != {})

        self.max_degree = max(self.G.degree[cell]
                              for cell in self.cell_list)
        self.max_net_degree = max(self.G.degree[net]
                                  for net in self.net_list)

    def number_of_cells(self):
        """[summary]

        Returns:
            [type] -- [description]
        """
        return len(self.cell_list)

    def number_of_nets(self):
        """[summary]

        Returns:
            [type] -- [description]
        """
        return len(self.net_list)

    def number_of_pins(self):
        """[summary]

        Returns:
            [type] -- [description]
        """
        return self.G.number_of_edges()

    def get_max_degree(self):
        """[summary]

        Returns:
            [type] -- [description]
        """
        return self.max_degree

    def get_max_net_degree(self):
        """[summary]

        Returns:
            [type] -- [description]
        """
        return self.max_net_degree
