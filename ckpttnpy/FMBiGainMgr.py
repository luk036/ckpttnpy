from .dllist import dllink
from .bpqueue import bpqueue
from .FMBiGainCalc import FMBiGainCalc


class FMBiGainMgr:

    # public:

    def __init__(self, H):
        """initialization

        Arguments:
            module_dict {dict} -- [description]
        """
        self.H = H
        self.gainCalc = FMBiGainCalc(H)
        self.pmax = self.H.get_max_degree()
        num_modules = H.number_of_modules()
        self.vertex_list = [dllink(i) for i in range(num_modules)]
        self.waitinglist = dllink(3734)
        self.gainbucket = bpqueue(-self.pmax, self.pmax)

    def init(self, part):
        """(re)initialization after creation

        Arguments:
            part {list} -- [description]
        """
        self.gainCalc.init(part, self.vertex_list)

        for v in self.H.module_fixed:
            # i_v = self.H.module_dict[v]
            # force to the lowest gain
            self.vertex_list[v].key = -self.pmax

        self.gainbucket.appendfrom(self.vertex_list)

    def is_empty_togo(self, toPart):
        return self.gainbucket.is_empty()

    def is_empty(self):
        """[summary]

        Returns:
            [type] -- [description]
        """
        return self.gainbucket.is_empty()

    def select(self, part):
        """[summary]

        Returns:
            [type] -- [description]
        """
        gainmax = self.gainbucket.get_max()
        vlink = self.gainbucket.popleft()
        self.waitinglist.append(vlink)
        v = vlink.idx
        fromPart = part[v]
        move_info_v = fromPart, 1-fromPart, v
        return move_info_v, gainmax

    def select_togo(self, toPart):
        gainmax = self.gainbucket.get_max()
        vlink = self.gainbucket.popleft()
        self.waitinglist.append(vlink)
        return vlink.idx, gainmax

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
        self.gainbucket.set_key(self.vertex_list[v], -gain)

    # private

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
        self.gainbucket.modify_key(self.vertex_list[w], deltaGainW)

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
            self.gainbucket.modify_key(
                self.vertex_list[IdVec[idx]], deltaGain[idx])
