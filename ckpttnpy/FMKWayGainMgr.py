from .dllist import dllink
from .bpqueue import bpqueue
from .FMKWayGainCalc import FMKWayGainCalc


class FMKWayGainMgr:

    # public:

    def __init__(self, H, K):
        """initialization

        Arguments:
            cell_dict {dict} -- [description]
        """
        self.H = H
        self.K = K
        self.gainCalc = FMKWayGainCalc(H, K)
        self.pmax = self.H.get_max_degree()
        num_cells = H.number_of_cells()
        self.gainbucket = []
        self.vertex_list = []
        for _ in range(K):
            self.gainbucket += [ bpqueue(-self.pmax, self.pmax) ]
            self.vertex_list += [ list(dllink(i) for i in range(num_cells)) ]
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
            for k in range(self.K):
                self.vertex_list[k][v].key = -self.pmax

        for v in self.H.cell_list:
            for k in range(self.K):
                vlink = self.vertex_list[k][v]
                if part[v] == k:
                    self.waitinglist.append(vlink)
                else:
                    self.gainbucket[k].append(vlink, vlink.key)

    def is_empty(self, toPart):
        return self.gainbucket[toPart].is_empty()

    def select_togo(self, toPart):
        gainmax = self.gainbucket[toPart].get_max()
        vlink = self.gainbucket[toPart].popleft()
        self.waitinglist.append(vlink)
        return vlink.idx, gainmax

    def set_key(self, whichPart, v, key):
        self.gainbucket[whichPart].set_key(
            self.vertex_list[whichPart][v], key)

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

        # i_v = self.H.cell_dict[v]
        # gain = self.gainbucket.get_key(self.vertex_list[v])
        # self.gainbucket.modify_key(self.vertex_list[v], -2*gain)
        self.set_key(fromPart, v, -gain)
        self.set_key(toPart, v, 0) # actually don't care

    # private:

    def modify_key(self, w, keys):
        for k in range(self.K):
            self.gainbucket[k].modify_key(
                self.vertex_list[k][w], keys[k])

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
        self.modify_key(w, deltaGainW)

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
            self.modify_key(IdVec[idx], deltaGain[idx])
