class Netlist:
    num_pads = 0
    cost_model = 0
    net_weight = []
    module_weight = []
    module_fixed = {}
    module_name = []

    def __init__(self, G, module_list, net_list):
        """[summary]

        Arguments:
            G {[type]} -- [description]
            module_list {[type]} -- [description]
            net_list {[type]} -- [description]

        Keyword Arguments:
            module_fixed {dict} -- [description] (default: {{}})
        """
        self.G = G
        self.module_list = module_list
        self.net_list = net_list
        self.num_modules = len(self.module_list)
        self.num_nets = len(self.net_list)

        # self.module_dict = {}
        # for i_v, v in enumerate(self.module_list):
        #     self.module_dict[v] = i_v

        # self.module_fixed = module_fixed
        self.has_fixed_modules = (self.module_fixed != {})

        self.max_degree = max(self.G.degree[module]
                              for module in self.module_list)
        self.max_net_degree = max(self.G.degree[net]
                                  for net in self.net_list)

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
        return 1 if self.module_weight == [] else self.module_weight[v]

    def get_net_weight(self, n):
        return 1 if self.net_weight == [] else self.net_weight[n - self.num_modules]
