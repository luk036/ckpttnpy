import networkx as nx


class ThinGraph(nx.Graph):
    all_edge_dict = {"weight": 1}

    def single_edge_dict(self):
        return self.all_edge_dict
    edge_attr_dict_factory = single_edge_dict


class Netlist:
    num_pads = 0
    cost_model = 0
    net_weight = []
    module_weight = []
    module_fixed = {}
    module_name = []

    parent = None
    node_up_map = {}
    node_down_map = {}
    cluster_down_map = {}

    def __init__(self, G, modules, nets, module_map, net_map):
        """[summary]

        Arguments:
            G {[type]} -- [description]
            module_list {[type]} -- [description]
            net_list {[type]} -- [description]

        Keyword Arguments:
            module_fixed {dict} -- [description] (default: {{}})
        """
        self.G = G
        self.modules = modules
        self.nets = nets
        self.module_map = module_map
        self.net_map = net_map
        self.num_modules = len(modules)
        self.num_nets = len(nets)

        # self.module_dict = {}
        # for v in enumerate(self.module_list):
        #     self.module_dict[v] = v

        # self.net_dict = {}
        # for i_net, net in enumerate(self.net_list):
        #     self.net_dict[net] = i_net

        # self.module_fixed = module_fixed
        self.has_fixed_modules = (self.module_fixed != {})

        self.max_degree = max(self.G.degree[cell] for cell in modules)
        self.max_net_degree = max(self.G.degree[net] for net in nets)

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
            v {size_t} -- [description]

        Returns:
            [size_t] -- [description]
        """
        i_v = self.module_map[v]
        return 1 if self.module_weight == [] \
            else self.module_weight[i_v]

    def get_module_weight_by_id(self, i_v):
        """[summary]

        Arguments:
            v {size_t} -- [description]

        Returns:
            [size_t] -- [description]
        """
        return 1 if self.module_weight == [] \
            else self.module_weight[i_v]

    def get_net_weight(self, net):
        """[summary]

        Arguments:
            i_net {size_t} -- [description]

        Returns:
            size_t -- [description]
        """
        # return 1 if self.net_weight == [] \
        #          else self.net_weight[self.net_map[net]]
        return 1

    # def project_down(self, part, part_down):
    #     H = self.parent
    #     for i_v, v in enumerate(self.modules):
    #         if v in self.cluster_down_map:
    #             net = self.cluster_down_map[v]
    #             for v2 in H.G[net]:
    #                 i_v2 = H.module_map[v2]
    #                 part_down[i_v2] = part[i_v]
    #         else:
    #             v2 = self.node_down_map[v]
    #             i_v2 = H.module_map[v2]
    #             part_down[i_v2] = part[i_v]

    # def project_up(self, part, part_up):
    #     H = self.parent
    #     for i_v, v in enumerate(H.modules):
    #         part_up[self.node_up_map[v]] = part[i_v]

    def projection_down(self, part, part_down):
        H = self.parent
        # part, extern_nets = part_info
        # part_down, extern_nets_down = part_info_down

        for i_v, v in enumerate(self.modules):
            if v in self.cluster_down_map:
                net = self.cluster_down_map[v]
                for v2 in H.G[net]:
                    i_v2 = H.module_map[v2]
                    part_down[i_v2] = part[i_v]
            else:
                v2 = self.node_down_map[v]
                i_v2 = H.module_map[v2]
                part_down[i_v2] = part[i_v]

        # if not extern_nets:
        #     return

        # extern_nets_down.clear()
        # for net in extern_nets:
        #     extern_nets_down.add(self.node_down_map[net])

    def projection_up(self, part, part_up):
        H = self.parent
        # part, extern_nets = part_info
        # part_up, extern_nets_up = part_info_up

        for i_v, v in enumerate(H.modules):
            part_up[self.node_up_map[v]] = part[i_v]

        # if not extern_nets:
        #     return

        # extern_nets_up.clear()
        # for net in extern_nets:
        #     extern_nets_up.add(self.node_up_map[net])

        # K = len(extern_modules)
        # extern_modules_up = list(set() for _ in K)

        # for k in range(K):
        #     for v in extern_modules[k]:
        #         v2 = self.node_up_map[v]
        #         extern_modules_up[k].add(v2)
