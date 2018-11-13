from dllist import dllink
from bpqueue import bpqueue
from netlist import Netlist


class FMBiGainMgr:
    H = Netlist()
    vertex_list = []

    def __init__(self, cell_dict):
        self.cell_dict = cell_dict

        pmax = self.H.get_max_degree()
        self.gainbucket = bpqueue(-pmax, pmax)

        num_cells = len(self.H.cell_list)
        self.vertex_list = [dllink(i) for i in range(num_cells)]

        self.num = [0, 0]

    def init(self, part):
        for net in self.H.net_list:
            self.init_gain(net, part)
        self.gainbucket.appendfrom(self.vertex_list)

    def init_gain(self, net, part):
        if self.H.G.out_degree[net] == 2:
            self.init_gain_2pin_net(net, part)
        else:
            self.init_gain_general_net(net, part)

    def init_gain_2pin_net(self, net, part):
        assert self.H.G.out_degree[net] == 2
        netCur = iter(self.H.G[net])
        w = next(netCur)
        v = next(netCur)
        i_w = self.cell_dict[w]
        i_v = self.cell_dict[v]
        part_w = part[i_w]
        part_v = part[i_v]
        weight = self.H.G[net].get('weight', 1)
        g = -weight if part_w == part_v else weight
        self.vertex_list[i_w].key += g
        self.vertex_list[i_v].key += g

    def init_gain_general_net(self, net, part):
        self.num = [0, 0]
        IdVec = []
        for w in self.H.G[net]:
            i_w = self.cell_dict[w]
            self.num[part[i_w]] += 1
            IdVec.append(i_w)

        weight = self.H.G[net].get('weight', 1)
        for k in [0, 1]:
            if self.num[k] == 0:
                for i_w in IdVec:
                    self.vertex_list[i_w].key -= weight
            elif self.num[k] == 1:
                for i_w in IdVec:
                    part_w = part[i_w]
                    if part_w == k:
                        self.vertex_list[i_w].key += weight
                        break

    def updateMove2PinNet(self, net, part, fromPart, v):
        assert self.H.G.out_degree[net] == 2
        netCur = iter(self.H.G[net])
        w = next(netCur)
        if w == v:
            w = next(netCur)
        i_w = self.cell_dict[w]
        part_w = part[i_w]
        weight = self.H.G[net].get('weight', 1)
        deltaGainW = 2*weight if part_w == fromPart else -2*weight
        self.gainbucket.modify_key(self.vertex_list[i_w], deltaGainW)

    def updateMoveGeneralNet(self, net, part, fromPart, v):
        assert self.H.G.out_degree[net] > 2

        IdVec = []
        deltaGain = []
        for w in self.H.G[net]:
            if w == v:
                continue
            IdVec.append(self.cell_dict[w])
            deltaGain.append(0)
        degree = len(IdVec)
        m = self.H.G[net].get('weight', 1)
        weight = m if fromPart == 0 else -m
        for k in [0, 1]:
            if self.num[k] == 0:
                for idx in range(degree):
                    deltaGain[idx] -= weight
            elif self.num[k] == 1:
                for idx in range(degree):
                    part_w = part[IdVec[idx]]
                    if part_w == k:
                        deltaGain[idx] += weight
                        break
            weight = -weight

        for idx in range(degree):
            self.gainbucket.modify_key(
                self.vertex_list[IdVec[idx]], deltaGain[idx])
