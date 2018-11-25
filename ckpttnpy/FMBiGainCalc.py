# from .dllist import dllink
# from .bpqueue import bpqueue


class FMBiGainCalc:

    # public:

    def __init__(self, H):
        """initialization

        Arguments:
            cell_dict {dict} -- [description]
        """
        self.H = H

    def init(self, part, vertex_list):
        """(re)initialization after creation

        Arguments:
            part {list} -- [description]
        """
        for net in self.H.net_list:
            self.init_gain(net, part, vertex_list)

    def init_gain(self, net, part, vertex_list):
        """initialize gain

        Arguments:
            net {Graph's node} -- [description]
            part {list} -- [description]
        """
        if self.H.G.degree[net] == 2:
            self.init_gain_2pin_net(net, part, vertex_list)
        elif self.H.G.degree[net] < 2:  # unlikely, self-loop, etc.
            return  # does not provide any gain when move
        else:
            self.init_gain_general_net(net, part, vertex_list)

    def init_gain_2pin_net(self, net, part, vertex_list):
        """initialize gain for 2-pin net

        Arguments:
            net {Graph's node} -- [description]
            part {list} -- [description]
        """
        assert self.H.G.degree[net] == 2
        netCur = iter(self.H.G[net])
        w = next(netCur)
        v = next(netCur)
        part_w = part[w]
        part_v = part[v]
        weight = self.H.G.nodes[net].get('weight', 1)
        g = -weight if part_w == part_v else weight

        vertex_list[w].key += g
        vertex_list[v].key += g

    def init_gain_general_net(self, net, part, vertex_list):
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
                for w in IdVec:
                    vertex_list[w].key -= weight
            elif num[k] == 1:
                for w in IdVec:
                    if part[w] == k:
                        vertex_list[w].key += weight
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
        return w, deltaGainW
        # self.gainbucket[1-part_w].modify_key(self.vertex_list[w], deltaGainW)

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
            if w == v:
                continue
            # i_w = self.H.cell_dict[w]
            num[part[w]] += 1
            IdVec.append(w)

        degree = len(IdVec)
        deltaGain = list(0 for _ in range(degree))
        weight = self.H.G.nodes[net].get('weight', 1)
        # weight = m if fromPart == 0 else -m
        toPart = 1 - fromPart
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