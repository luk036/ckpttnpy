from .bpqueue import bpqueue
from .dllist import dllink
from abc import abstractmethod


class FMGainMgr:

    # public:

    def __init__(self, H, GainCalc, K=2):
        """initialiation

        Arguments:
            H {Netlist} -- [description]
            GainCalc {[type]} -- [description]

        Keyword Arguments:
            K {int} -- number of partitions (default: {2})
        """
        self.H = H
        self.K = K
        self.gainCalc = GainCalc
        self.pmax = self.H.get_max_degree()
        self.waitinglist = dllink(3734)
        self.gainbucket = []
        for _ in range(K):
            self.gainbucket += [bpqueue(-self.pmax, self.pmax)]

    def init(self, part):
        """(re)initialization after creation

        Arguments:
            part {list} -- [description]
        """
        self.gainCalc.init(part)

        for v in self.H.module_fixed:
            # force to the lowest gain
            self.gainCalc.set_key(v, -self.pmax)

    def is_empty_togo(self, toPart):
        """[summary]

        Arguments:
            toPart {uint8_t} -- [description]

        Returns:
            bool -- [description]
        """
        return self.gainbucket[toPart].is_empty()

    def is_empty(self):
        """Any more candidate?

        Returns:
            bool -- [description]
        """
        for k in range(self.K):
            if not self.gainbucket[k].is_empty():
                return False
        return True

    def select(self, part):
        """Select best candidate

        Arguments:
            part {list} -- [description]

        Returns:
            move_info_v -- [description]
        """
        gainmax = list(self.gainbucket[k].get_max() for k in range(self.K))
        maxk = max(gainmax)
        toPart = gainmax.index(maxk)
        vlink = self.gainbucket[toPart].popleft()
        self.waitinglist.append(vlink)
        i_v = vlink.idx
        v = self.H.modules[i_v]
        fromPart = part[i_v]
        move_info_v = fromPart, toPart, v, i_v
        return move_info_v, gainmax[toPart]

    def select_togo(self, toPart):
        """Select best candidaate togo

        Arguments:
            toPart {uint8_t} -- [description]

        Returns:
            node_t -- [description]
        """
        gainmax = self.gainbucket[toPart].get_max()
        vlink = self.gainbucket[toPart].popleft()
        self.waitinglist.append(vlink)
        i_v = vlink.idx
        return self.H.modules[i_v], i_v, gainmax

    def update_move(self, part, move_info_v):
        """[summary]

        Arguments:
            part {list} -- [description]
            move_info_v {[type]} -- [description]
        """
        # self.deltaGainV = list(0 for _ in range(self.K))
        self.gainCalc.update_move_init()

        fromPart, toPart, v, _ = move_info_v
        for net in self.H.G[v]:
            move_info = [net, fromPart, toPart, v]
            if self.H.G.degree[net] == 2:
                self.update_move_2pin_net(part, move_info)
            elif self.H.G.degree[net] < 2:  # unlikely, self-loop, etc.
                break  # does not provide any gain change when move
            else:
                self.update_move_general_net(part, move_info)

    # private:

    @abstractmethod
    def modify_key(self, part, w, key):
        """Abstract method

        Arguments:
            part {uint8_t} -- [description]
            w {node_t} -- [description]
            key {int/int[]} -- [description]
        """

    def update_move_2pin_net(self, part, move_info):
        """Update move for 2-pin net

        Arguments:
            part {list} -- Partition sol'n
            move_info {[type]} -- [description]
        """
        i_w, deltaGainW = self.gainCalc.update_move_2pin_net(
            part, move_info)
        self.modify_key(part, i_w, deltaGainW)

    def update_move_general_net(self, part, move_info):
        """Update move for general net

        Arguments:
            part {list} -- Partition sol'n
            move_info {[type]} -- [description]
        """
        IdVec, deltaGain = self.gainCalc.update_move_general_net(
            part, move_info)
        degree = len(IdVec)
        for idx in range(degree):
            self.modify_key(part, IdVec[idx], deltaGain[idx])
