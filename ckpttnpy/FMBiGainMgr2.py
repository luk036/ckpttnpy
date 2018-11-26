from .dllist import dllink
from .bpqueue import bpqueue
from .FMBiGainCalc import FMBiGainCalc


class FMBiGainMgr2:

    # public:

    def __init__(self, H):
        """initialization

        Arguments:
            cell_dict {dict} -- [description]
        """
        self.H = H
        self.gainCalc = FMBiGainCalc(H)
        self.pmax = self.H.get_max_degree()
        self.gainbucket = []
        for _ in [0, 1]:
            self.gainbucket += [bpqueue(-self.pmax, self.pmax)]
        num_cells = H.number_of_cells()
        self.vertex_list = [dllink(i) for i in range(num_cells)]
        self.waitinglist = dllink(3734)
        # num = [0, 0]

    def init(self, part):
        """(re)initialization after creation

        Arguments:
            part {list} -- [description]
        """
        self.gainCalc.init(part, self.vertex_list)

        for v in self.H.cell_fixed:
            # i_v = self.H.cell_dict[v]
            # force to the lowest gain
            self.vertex_list[v].key = -self.pmax

        for v in self.H.cell_list:
            vlink = self.vertex_list[v]
            toPart = 1 - part[v]
            self.gainbucket[toPart].append(vlink, vlink.key)

    def is_empty(self):
        for k in [0, 1]:
            if not self.gainbucket[k].is_empty():
                return False
        return True

    def select(self):
        gainmax = [0, 0]
        for k in [0, 1]:
            gainmax[k] = self.gainbucket[k].get_max()
        toPart = 0 if gainmax[0] > gainmax[1] else 1
        vlink = self.gainbucket[toPart].popleft()
        self.waitinglist.append(vlink)
        return vlink.idx, gainmax[toPart]

    def update_move(self, part, move_info_v, gain):
        """[summary]

        Arguments:
            part {[type]} -- [description]
            v {[type]} -- [description]
        """
        fromPart, toPart, v = move_info_v
        for net in self.H.G[v]:
            move_info = [net, fromPart, toPart, v]
            if self.H.G.degree[net] == 2:
                self.update_move_2pin_net(part, move_info)
            elif self.H.G.degree[net] < 2:  # unlikely, self-loop, etc.
                break  # does not provide any gain change when move
            else:
                self.update_move_general_net(part, move_info)

        # self.vertex_list[v].key -= 2*gain
        self.gainbucket[toPart].set_key(self.vertex_list[v], -gain)

    # private:

    def update_move_2pin_net(self, part, move_info):
        """Update move for 2-pin net

        Arguments:
            net {Graph's node} -- [description]
            part {list} -- [description]
            fromPart {int} -- [description]
            v {Graph's node} -- [description]
        """
        w, deltaGainW = self.gainCalc.update_move_2pin_net(
            part, move_info)
        part_w = part[w]
        self.gainbucket[1-part_w].modify_key(self.vertex_list[w], deltaGainW)

    def update_move_general_net(self, part, move_info):
        """update move for general net

        Arguments:
            net {Graph's node} -- [description]
            part {list} -- [description]
            fromPart {int} -- [description]
            v {Graph's node} -- [description]
        """
        IdVec, deltaGain = self.gainCalc.update_move_general_net(
            part, move_info)
        degree = len(IdVec)
        for idx in range(degree):
            part_w = part[IdVec[idx]]
            self.gainbucket[1-part_w].modify_key(
                self.vertex_list[IdVec[idx]], deltaGain[idx])
