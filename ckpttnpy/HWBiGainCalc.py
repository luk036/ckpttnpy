from .dllist import dllink
# from .bpqueue import bpqueue


class HWBiGainCalc:

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
        self.vertex_list = list(dllink(i)
                                for i in range(self.H.number_of_modules()))
        self.totalcost = 0

    def init(self, soln_info):
        """(re)initialization after creation

        Arguments:
            part {list} -- [description]
        """
        self.totalcost = 0
        for vlink in self.vertex_list:
            vlink.key = 0
        for net in self.H.nets:
            # for net in self.H.net_list:
            self.init_gain(net, soln_info)

    def init_gain(self, net, soln_info):
        """initialize gain

        Arguments:
            net {node_t} -- [description]
            part {list} -- [description]
        """
        if self.H.G.degree[net] < 2:  # unlikely, self-loop, etc.
            return  # does not provide any gain when move
        part, extern_nets = soln_info
        weight = self.H.get_net_weight(net)
        if net in extern_nets:
            self.totalcost += weight
            if self.H.G.degree[net] == 2:
                for w in self.H.G[net]:
                    # w = self.H.module_map[w]
                    self.modify_gain(w, weight)
            else:
                self.init_gain_general_net(net, part, weight)
        else: # 90%
            for w in self.H.G[net]:
                # w = self.H.module_map[w]
                self.modify_gain(w, -weight)

    def init_gain_general_net(self, net, part, weight):
        """initialize gain for general net

        Arguments:
            net {node_t} -- [description]
            part {list} -- [description]
        """
        num = [0, 0]
        IdVec = []
        for w in self.H.G[net]:
            # w = self.H.module_map[w]
            num[part[w]] += 1
            IdVec.append(w)

        for k in [0, 1]:
            if num[k] == 1:
                for w in IdVec:
                    if part[w] == k:
                        self.modify_gain(w, weight)
                        break

    def set_key(self, v, weight, toPart=None):
        """[summary]

        Arguments:
            v {[type]} -- [description]
            key {[type]} -- [description]
        """
        # i_v = self.H.module_map[v]
        # assert i_v == v
        self.vertex_list[v].key = weight

    def modify_gain(self, w, weight):
        """Modify gain

        Arguments:
            v {node_t} -- [description]
            weight {int} -- [description]
        """
        self.vertex_list[w].key += weight

    def update_move_init(self):
        """update move init

           nothing to do in 2-way partitioning
        """
        pass

    def update_move_2pin_net(self, soln_info, move_info):
        """Update move for 2-pin net

        Arguments:
            part {list} -- [description]
            move_info {MoveInfoV} -- [description]

        Returns:
            [type] -- [description]
        """
        part, extern_nets, _ = soln_info
        net, fromPart, _, v = move_info
        assert self.H.G.degree[net] == 2
        netCur = iter(self.H.G[net])
        u = next(netCur)
        w = u if u != v else next(netCur)
        # w = self.H.module_map[w]
        part_w = part[w]
        weight = self.H.get_net_weight(net)
        if part_w == fromPart:
            deltaGainW = 2*weight
            extern_nets.add(net)
        else:
            deltaGainW = -2*weight
            extern_nets.remove(net)
        return w, deltaGainW

    def update_move_general_net(self, soln_info, move_info):
        """Update move for general net

        Arguments:
            part {list} -- [description]
            move_info {MoveInfoV} -- [description]

        Returns:
            [type] -- [description]
        """
        net, fromPart, toPart, v = move_info
        part, extern_nets, _ = soln_info
        assert self.H.G.degree[net] > 2
        num = [0, 0]
        IdVec = []
        deltaGain = []
        for w in self.H.G[net]:
            if w == v:
                continue
            # w = self.H.module_map[w]
            num[part[w]] += 1
            IdVec.append(w)

        degree = len(IdVec)
        deltaGain = list(0 for _ in range(degree))
        weight = self.H.get_net_weight(net)

        if num[fromPart] == 0:
            extern_nets.remove(net)
            for idx in range(degree):
                deltaGain[idx] -= weight
            return IdVec, deltaGain
            
        if num[toPart] == 0:
            extern_nets.add(net)
            for idx in range(degree):
                deltaGain[idx] += weight
            return IdVec, deltaGain

        for l in [fromPart, toPart]:
            if num[l] == 1:
                for idx in range(degree):
                    part_w = part[IdVec[idx]]
                    if part_w == l:
                        deltaGain[idx] += weight
                        break
            weight = -weight

        return IdVec, deltaGain
