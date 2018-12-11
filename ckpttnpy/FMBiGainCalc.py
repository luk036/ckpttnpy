from .dllist import dllink
# from .bpqueue import bpqueue


class FMBiGainCalc:

    # public:

    def __init__(self, H, K=2):
        """Initialization

        Arguments:
            H {Netlist} -- [description]

        Keyword Arguments:
            K {uint8_t} -- number of partitions (default: {2})
        """
        self.H = H
        self.vertex_list = []
        self.vertex_list = list(dllink(i) for i in H.modules)

    def init(self, part):
        """(re)initialization after creation

        Arguments:
            part {list} -- [description]
        """
        for net in self.H.nets:
        # for net in self.H.net_list:
            self.init_gain(net, part)

    def init_gain(self, net, part):
        """initialize gain

        Arguments:
            net {node_t} -- [description]
            part {list} -- [description]
        """
        if self.H.G.degree[net] == 2:
            self.init_gain_2pin_net(net, part)
        elif self.H.G.degree[net] < 2:  # unlikely, self-loop, etc.
            return  # does not provide any gain when move
        else:
            self.init_gain_general_net(net, part)

    def set_key(self, v, weight, toPart=None):
        """[summary]

        Arguments:
            v {[type]} -- [description]
            key {[type]} -- [description]
        """
        self.vertex_list[self.H.module_map[v]].key = weight

    def modify_gain(self, v, weight, toPart=None):
        """Modify gain

        Arguments:
            v {node_t} -- [description]
            weight {int} -- [description]
        """
        self.vertex_list[self.H.module_map[v]].key += weight

    def init_gain_2pin_net(self, net, part):
        """initialize gain for 2-pin net

        Arguments:
            net {node_t} -- [description]
            part {list} -- [description]
        """
        assert self.H.G.degree[net] == 2
        netCur = iter(self.H.G[net])
        w = next(netCur)
        v = next(netCur)
        part_w = part[self.H.module_map[w]]
        part_v = part[self.H.module_map[v]]
        weight = self.H.get_net_weight(net)

        g = -weight if part_w == part_v else weight
        self.modify_gain(w, g)
        self.modify_gain(v, g)

    def init_gain_general_net(self, net, part):
        """initialize gain for general net

        Arguments:
            net {node_t} -- [description]
            part {list} -- [description]
        """
        num = [0, 0]
        IdVec = []
        for w in self.H.G[net]:
            # i_w = self.H.module_dict[self.H.module_map[w]]
            num[part[self.H.module_map[w]]] += 1
            IdVec.append(w)

        weight = self.H.get_net_weight(net)

        for k in [0, 1]:
            if num[k] == 0:
                for w in IdVec:
                    self.modify_gain(w, -weight)
            elif num[k] == 1:
                for w in IdVec:
                    if part[self.H.module_map[w]] == k:
                        self.modify_gain(w, weight)
                        break

    def update_move_init(self):
        """update move init

           nothing to do in 2-way partitioning
        """
        pass

    def update_move_2pin_net(self, part, move_info):
        """Update move for 2-pin net

        Arguments:
            part {list} -- [description]
            move_info {MoveInfoV} -- [description]

        Returns:
            [type] -- [description]
        """
        net, fromPart, _, v = move_info
        assert self.H.G.degree[net] == 2
        netCur = iter(self.H.G[net])
        u = next(netCur)
        w = u if u != v else next(netCur)
        # i_w = self.H.module_dict[self.H.module_map[w]]
        part_w = part[self.H.module_map[w]]
        weight = self.H.get_net_weight(net)
        deltaGainW = 2*weight if part_w == fromPart else -2*weight
        return w, deltaGainW

    def update_move_general_net(self, part, move_info):
        """Update move for general net

        Arguments:
            part {list} -- [description]
            move_info {MoveInfoV} -- [description]

        Returns:
            [type] -- [description]
        """
        net, fromPart, toPart, v = move_info
        assert self.H.G.degree[net] > 2
        num = [0, 0]
        IdVec = []
        deltaGain = []
        for w in self.H.G[net]:
            if w == v:
                continue
            # i_w = self.H.module_dict[self.H.module_map[w]]
            num[part[self.H.module_map[w]]] += 1
            IdVec.append(w)

        degree = len(IdVec)
        deltaGain = list(0 for _ in range(degree))
        weight = self.H.get_net_weight(net)

        for l in [fromPart, toPart]:
            if num[l] == 0:
                for idx in range(degree):
                    deltaGain[idx] -= weight
            elif num[l] == 1:
                for idx in range(degree):
                    part_w = part[IdVec[idx]]
                    if part_w == l:
                        deltaGain[idx] += weight
                        break
            weight = -weight

        return IdVec, deltaGain
