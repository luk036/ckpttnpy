from .dllist import dllink
from .robin import robin


class FDKWayGainCalc:

    # public:

    def __init__(self, H, K):
        """initialization

        Arguments:
            H {Netlist} -- [description]
            K {uint8_t} -- number of partitions
        """
        self.H = H
        self.K = K
        self.RR = robin(K)
        self.totalcost = 0

        self.vertex_list = []
        for _ in range(K):
            self.vertex_list += [list(dllink(i)
                                      for i in range(self.H.number_of_modules()))]
        self.deltaGainV = list()

    def init(self, part_info):
        """(re)initialization after creation

        Arguments:
            part {list} -- [description]
        """
        self.totalcost = 0
        for k in range(self.K):
            for vlink in self.vertex_list[k]:
                vlink.key = 0

        for net in self.H.nets:
            self.init_gain(net, part_info)

    def init_gain(self, net, part_info):
        """initialize gain

        Arguments:
            net {node_t} -- [description]
            part {list} -- [description]
        """
        if self.H.G.degree[net] < 2:  # unlikely, self-loop, etc.
            return  # does not provide any gain when move
        part, extern_nets = part_info
        weight = self.H.get_net_weight(net)
        if net in extern_nets:
            # self.totalcost += weight
            if self.H.G.degree[net] == 2:
                self.init_gain_2pin_net(net, part)
            else:
                self.init_gain_general_net(net, part)
        else: # 90%
            for w in self.H.G[net]:
                for k in self.RR.exclude(part[w]):
                    self.vertex_list[k][w].key -= weight

    def set_key(self, v, key):
        """[summary]

        Arguments:
            v {[type]} -- [description]
            key {[type]} -- [description]
        """
        # v = self.H.module_map[v]
        for k in range(self.K):
            self.vertex_list[k][v].key = key

    def modify_gain(self, v, part_v, weight):
        """Modify gain

        Arguments:
            v {node_t} -- [description]
            weight {int} -- [description]
        """
        for k in self.RR.exclude(part_v):
            self.vertex_list[k][v].key += weight

    def init_gain_2pin_net(self, net, part):
        """initialize gain for 2-pin net

        Arguments:
            net {node_t} -- [description]
            part {list} -- [description]
        """
        assert self.H.G.degree[net] == 2
        weight = self.H.get_net_weight(net)
        self.totalcost += weight
        netCur = iter(self.H.G[net])
        w = next(netCur)
        v = next(netCur)
        # w = self.H.module_map[w]
        # v = self.H.module_map[v]
        part_w = part[w]
        part_v = part[v]
        self.vertex_list[part_v][w].key += weight
        self.vertex_list[part_w][v].key += weight

    def init_gain_general_net(self, net, part):
        """initialize gain for general net

        Arguments:
            net {node_t} -- [description]
            part {list} -- [description]
        """
        num = list(0 for _ in range(self.K))
        IdVec = []
        for w in self.H.G[net]:
            # w = self.H.module_map[w]
            num[part[w]] += 1
            IdVec.append(w)

        weight = self.H.get_net_weight(net)
        for k in range(self.K):
            if num[k] > 0:
                self.totalcost += weight
                if num[k] == 1:
                    for w in IdVec:
                        if part[w] == k:
                            self.modify_gain(w, part[w], weight)
                            break
            else: # num[k] == 0
                for w in IdVec:
                    self.vertex_list[k][w].key -= weight
        self.totalcost -= weight

    def update_move_init(self):
        """update move init
        """
        self.deltaGainV = list(0 for _ in range(self.K))

    def update_move_2pin_net(self, part_info, move_info):
        """Update move for 2-pin net

        Arguments:
            part {list} -- [description]
            move_info {MoveInfoV} -- [description]

        Returns:
            [type] -- [description]
        """
        net, fromPart, toPart, v = move_info
        assert self.H.G.degree[net] == 2
        part, extern_nets = part_info
        netCur = iter(self.H.G[net])
        u = next(netCur)
        w = u if u != v else next(netCur)
        # w = self.H.module_map[w]
        part_w = part[w]
        weight = self.H.get_net_weight(net)
        deltaGainW = list(0 for _ in range(self.K))
        # deltaGainV = list(0 for _ in range(self.K))
        if part_w == fromPart:
            extern_nets.add(net)
            for k in range(self.K):
                deltaGainW[k] += weight
                self.deltaGainV[k] += weight
        elif part_w == toPart:
            extern_nets.remove(net)
            for k in range(self.K):
                deltaGainW[k] -= weight
                self.deltaGainV[k] -= weight

        deltaGainW[fromPart] -= weight
        deltaGainW[toPart] += weight
        return w, deltaGainW

    def update_move_general_net(self, part_info, move_info):
        """Update move for general net

        Arguments:
            part {list} -- [description]
            move_info {MoveInfoV} -- [description]

        Returns:
            [type] -- [description]
        """
        net, fromPart, toPart, v = move_info
        assert self.H.G.degree[net] > 2
        part, extern_nets = part_info

        num = list(0 for _ in range(self.K))
        IdVec = []
        deltaGain = []
        for w in self.H.G[net]:
            if w == v:
                continue
            # w = self.H.module_map[w]
            num[part[w]] += 1
            IdVec.append(w)

        degree = len(IdVec)
        deltaGain = list(list(0 for _ in range(self.K))
                         for _ in range(degree))
        # deltaGainV = list(0 for _ in range(self.K))

        weight = self.H.get_net_weight(net)

        count = 0
        for k in range(self.K):
            if num[k] > 0:
                count += 1

        if num[fromPart] == 0:
            if num[toPart] > 0:
                for k in range(self.K):
                    self.deltaGainV[k] -= weight
                if count == 1:
                    extern_nets.remove(net)
        else:
            if num[toPart] == 0:
                for k in range(self.K):
                    self.deltaGainV[k] += weight
                if count == 1:
                    extern_nets.add(net)

        for l in [fromPart, toPart]:
            if num[l] == 0:
                for idx in range(degree):
                    deltaGain[idx][l] -= weight
            elif num[l] == 1:
                for idx in range(degree):
                    part_w = part[IdVec[idx]]
                    if part_w == l:
                        for k in range(self.K):
                            deltaGain[idx][k] += weight
                        break
            weight = -weight

        return IdVec, deltaGain
