from .dllist import dllink
from .bpqueue import bpqueue


class FMBiGainMgr:

    # public:

    def __init__(self, H):
        """initialization

        Arguments:
            cell_dict {dict} -- [description]
        """
        self.H = H
        self.pmax = self.H.get_max_degree()
        self.gainbucket = bpqueue(-self.pmax, self.pmax)

        num_cells = H.number_of_cells()
        self.vertex_list = [dllink(i) for i in range(num_cells)]
        self.waitinglist = dllink(3734)
        # num = [0, 0]

    def popleft(self):
        gainmax = self.gainbucket.get_max()
        vlink = self.gainbucket.popleft()
        self.waitinglist.append(vlink)
        return vlink.idx, gainmax

    def init(self, part):
        """(re)initialization after creation

        Arguments:
            part {list} -- [description]
        """
        for net in self.H.net_list:
            self.init_gain(net, part)

        for v in self.H.cell_fixed:
            # i_v = self.H.cell_dict[v]
            # force to the lowest gain
            self.vertex_list[v].key = -self.pmax

        self.gainbucket.appendfrom(self.vertex_list)

    def init_gain(self, net, part):
        """initialize gain

        Arguments:
            net {Graph's node} -- [description]
            part {list} -- [description]
        """
        if self.H.G.degree[net] == 2:
            self.init_gain_2pin_net(net, part)
        elif self.H.G.degree[net] < 2:  # unlikely, self-loop, etc.
            return  # does not provide any gain when move
        else:
            self.init_gain_general_net(net, part)

    def update_move(self, part, fromPart, v, gain):
        """[summary]

        Arguments:
            part {[type]} -- [description]
            v {[type]} -- [description]
        """
        for net in self.H.G[v]:
            if self.H.G.degree[net] == 2:
                self.update_move_2pin_net(net, part, fromPart, v)
            elif self.H.G.degree[net] < 2:  # unlikely, self-loop, etc.
                break  # does not provide any gain change when move
            else:
                self.update_move_general_net(net, part, fromPart, v)

        # i_v = self.H.cell_dict[v]
        # gain = self.gainbucket.get_key(self.vertex_list[v])
        # self.gainbucket.modify_key(self.vertex_list[v], -2*gain)
        self.vertex_list[v].key -= 2*gain

    # private:

    def init_gain_2pin_net(self, net, part):
        """initialize gain for 2-pin net

        Arguments:
            net {Graph's node} -- [description]
            part {list} -- [description]
        """
        assert self.H.G.degree[net] == 2
        netCur = iter(self.H.G[net])
        w = next(netCur)
        v = next(netCur)
        # i_w = self.H.cell_dict[w]
        # i_v = self.H.cell_dict[v]
        part_w = part[w]
        part_v = part[v]
        weight = self.H.G.nodes[net].get('weight', 1)
        g = -weight if part_w == part_v else weight
        self.vertex_list[w].key += g
        self.vertex_list[v].key += g

    def init_gain_general_net(self, net, part):
        """initialize gain for general net

        Arguments:
            net {Graph's node} -- [description]
            part {list} -- [description]
        """
        num = [0, 0]
        IdVec = []
        for w in self.H.G[net]:
            # i_w = self.H.cell_dict[w]
            num[part[w]] += 1
            IdVec.append(w)

        weight = self.H.G.nodes[net].get('weight', 1)
        for k in [0, 1]:
            if num[k] == 0:
                for i_w in IdVec:
                    self.vertex_list[i_w].key -= weight
            elif num[k] == 1:
                for i_w in IdVec:
                    part_w = part[i_w]
                    if part_w == k:
                        self.vertex_list[i_w].key += weight
                        break

    def update_move_2pin_net(self, net, part, fromPart, v):
        """Update move for 2-pin net

        Arguments:
            net {Graph's node} -- [description]
            part {list} -- [description]
            fromPart {int} -- [description]
            v {Graph's node} -- [description]
        """
        assert self.H.G.degree[net] == 2
        netCur = iter(self.H.G[net])
        u = next(netCur)
        w = u if u != v else next(netCur)
        # i_w = self.H.cell_dict[w]
        part_w = part[w]
        weight = self.H.G.nodes[net].get('weight', 1)
        deltaGainW = 2*weight if part_w == fromPart else -2*weight
        self.gainbucket.modify_key(self.vertex_list[w], deltaGainW)

    def update_move_general_net(self, net, part, fromPart, v):
        """update move for general net

        Arguments:
            net {Graph's node} -- [description]
            part {list} -- [description]
            fromPart {int} -- [description]
            v {Graph's node} -- [description]
        """
        assert self.H.G.degree[net] > 2

        num = [0, 0]
        IdVec = []
        deltaGain = []
        for w in self.H.G[net]:
            if w == v: continue
            # i_w = self.H.cell_dict[w]
            num[part[w]] += 1
            IdVec.append(w)
            deltaGain.append(0)
        degree = len(IdVec)

        m = self.H.G.nodes[net].get('weight', 1)
        weight = m if fromPart == 0 else -m
        for k in [0, 1]:
            if num[k] == 0:
                for idx in range(degree):
                    deltaGain[idx] -= weight
            elif num[k] == 1:
                for idx in range(degree):
                    part_w = part[IdVec[idx]]
                    if part_w == k:
                        deltaGain[idx] += weight
                        break
            weight = -weight

        for idx in range(degree):
            if deltaGain[idx] == 0:
                continue
            self.gainbucket.modify_key(
                self.vertex_list[IdVec[idx]], deltaGain[idx])
