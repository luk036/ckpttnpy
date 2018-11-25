from .dllist import dllink
from .bpqueue import bpqueue
from .FMBiGainCalc import FMBiGainCalc

class FMBiGainMgr:

    # public:

    def __init__(self, H):
        """initialization

        Arguments:
            cell_dict {dict} -- [description]
        """
        self.H = H
        self.gainCalc = FMBiGainCalc(H)
        self.pmax = self.H.get_max_degree()
        self.gainbucket = bpqueue(-self.pmax, self.pmax)
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

        self.gainbucket.appendfrom(self.vertex_list)

    def is_empty(self):
        """[summary]
        
        Returns:
            [type] -- [description]
        """
        return self.gainbucket.is_empty()

    def select(self):
        """[summary]
        
        Returns:
            [type] -- [description]
        """
        gainmax = self.gainbucket.get_max()
        vlink = self.gainbucket.popleft()
        self.waitinglist.append(vlink)
        return vlink.idx, gainmax

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
        self.vertex_list[v].key -= 2*gain

    def update_move_2pin_net(self, net, part, fromPart, v):
        """Update move for 2-pin net

        Arguments:
            net {Graph's node} -- [description]
            part {list} -- [description]
            fromPart {int} -- [description]
            v {Graph's node} -- [description]
        """
        w, deltaGainW = self.gainCalc.update_move_2pin_net(
            net, part, fromPart, v)
        self.gainbucket.modify_key(self.vertex_list[w], deltaGainW)

    def update_move_general_net(self, net, part, fromPart, v):
        """update move for general net

        Arguments:
            net {Graph's node} -- [description]
            part {list} -- [description]
            fromPart {int} -- [description]
            v {Graph's node} -- [description]
        """
        IdVec, deltaGain = self.gainCalc.update_move_general_net(
            net, part, fromPart, v)
        degree = len(IdVec)
        for idx in range(degree):
            self.gainbucket.modify_key(
                self.vertex_list[IdVec[idx]], deltaGain[idx])
