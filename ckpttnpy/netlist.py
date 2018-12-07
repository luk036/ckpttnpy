class Netlist:
    num_pads = 0
    cost_model = 0
    net_weight = []
    module_weight = []
    module_fixed = {}
    module_name = []

    def __init__(self, G, num_modules, num_nets):
        """[summary]

        Arguments:
            G {[type]} -- [description]
            module_list {[type]} -- [description]
            net_list {[type]} -- [description]

        Keyword Arguments:
            module_fixed {dict} -- [description] (default: {{}})
        """
        self.G = G
        self.num_modules = num_modules
        self.num_nets = num_nets

        # self.module_dict = {}
        # for i_v, v in enumerate(self.module_list):
        #     self.module_dict[v] = i_v

        # self.net_dict = {}
        # for i_net, net in enumerate(self.net_list):
        #     self.net_dict[net] = i_net

        # self.module_fixed = module_fixed
        self.has_fixed_modules = (self.module_fixed != {})

        self.max_degree = max(self.G.degree[module]
                              for module in range(num_modules))
        self.max_net_degree = max(self.G.degree[net]
                                  for net in range(num_modules, G.number_of_nodes()))

    def number_of_modules(self):
        """[summary]

        Returns:
            [type] -- [description]
        """
        return self.num_modules

    def number_of_nets(self):
        """[summary]

        Returns:
            [type] -- [description]
        """
        return self.num_nets

    def number_of_nodes(self):
        """[summary]

        Returns:
            [type] -- [description]
        """
        return self.G.number_of_nodes()

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

    def get_module_weight(self, v):
        """[summary]

        Arguments:
            i_v {size_t} -- [description]

        Returns:
            [size_t] -- [description]
        """
        return 1 if self.module_weight == [] else self.module_weight[v]

    def get_net_weight(self, net):
        """[summary]

        Arguments:
            i_net {size_t} -- [description]

        Returns:
            size_t -- [description]
        """
        return 1 if self.net_weight == [] else self.net_weight[net - self.num_modules]
