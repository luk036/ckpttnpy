from .dllist import dllink
from .bpqueue import bpqueue
from .FMKWayGainCalc import FMKWayGainCalc


class FMKWayGainMgr:

    # public:

    def __init__(self, H, K):
        """initialization

        Arguments:
            module_dict {dict} -- [description]
        """
        self.H = H
        self.K = K
        self.gainCalc = FMKWayGainCalc(H, K)
        self.pmax = self.H.get_max_degree()
        num_modules = H.number_of_modules()
        self.waitinglist = dllink(3734)

        self.gainbucket = []
        self.vertex_list = []
        for _ in range(K):
            self.gainbucket += [bpqueue(-self.pmax, self.pmax)]
            self.vertex_list += [list(dllink(i) for i in range(num_modules))]

        self.deltaGainV = list()

    def init(self, part):
        """(re)initialization after creation

        Arguments:
            part {list} -- [description]
        """
        self.gainCalc.init(part, self.vertex_list)

        for v in self.H.module_fixed:
            # i_v = self.H.module_dict[v]
            # force to the lowest gain
            for k in range(self.K):
                self.vertex_list[k][v].key = -self.pmax

        for v in self.H.module_list:
            for k in range(self.K):
                vlink = self.vertex_list[k][v]
                if part[v] == k:
                    assert vlink.key == 0
                    self.gainbucket[k].set_key(vlink, 0)
                    self.waitinglist.append(vlink)
                else:
                    self.gainbucket[k].append(vlink, vlink.key)

    def is_empty_togo(self, toPart):
        return self.gainbucket[toPart].is_empty()

    def is_empty(self):
        for k in range(self.K):
            if not self.gainbucket[k].is_empty():
                return False
        return True

    def select(self, part):
        gainmax = list(self.gainbucket[k].get_max() for k in range(self.K))
        maxk = max(gainmax)
        toPart = gainmax.index(maxk)
        vlink = self.gainbucket[toPart].popleft()
        self.waitinglist.append(vlink)
        v = vlink.idx
        fromPart = part[v]
        move_info_v = fromPart, toPart, v
        return move_info_v, gainmax[toPart]

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
        self.deltaGainV = list(0 for _ in range(self.K))

        fromPart, toPart, v = move_info_v
        for net in self.H.G[v]:
            move_info = [net, fromPart, toPart, v]
            if self.H.G.degree[net] == 2:
                self.update_move_2pin_net(part, move_info)
            elif self.H.G.degree[net] < 2:  # unlikely, self-loop, etc.
                break  # does not provide any gain change when move
            else:
                self.update_move_general_net(part, move_info)

        for k in range(self.K):
            if fromPart == k or toPart == k:
                continue
            self.gainbucket[k].modify_key(self.vertex_list[k][v],
                                          self.deltaGainV[k])
            # self.gainbucket[k].detach(self.vertex_list[k][v])
            # self.waitinglist.append(self.vertex_list[k][v])

        self.set_key(fromPart, v, -gain)
        self.set_key(toPart, v, 0)  # actually don't care

    # private:

    def modify_key(self, part, w, keys):
        for k in range(self.K):
            if part[w] == k:
                continue
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
            part, move_info, self.deltaGainV)
        self.modify_key(part, w, deltaGainW)

    def update_move_general_net(self, part, move_info):
        """update move for general net

        Arguments:
            net {Graph's node} -- [description]
            part {list} -- [description]
            fromPart {int} -- [description]
            v {Graph's node} -- [description]
        """
        IdVec, deltaGain = self.gainCalc.update_move_general_net(
            part, move_info, self.deltaGainV)
        degree = len(IdVec)
        for idx in range(degree):
            self.modify_key(part, IdVec[idx], deltaGain[idx])
