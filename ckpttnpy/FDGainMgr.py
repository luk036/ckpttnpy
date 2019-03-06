from .bpqueue import bpqueue
from .dllist import dllink
from abc import abstractmethod


class FDGainMgr:

    # public:

    def __init__(self, GainCalc, H, K=2):
        """initialiation

        Arguments:
            H {Netlist} -- [description]
            GainCalc {[type]} -- [description]

        Keyword Arguments:
            K {int} -- number of partitions (default: {2})
        """
        self.H = H
        self.K = K
        self.gainCalc = GainCalc(H, K)
        self.pmax = self.H.get_max_degree()
        self.waitinglist = dllink(3734)
        # self.totalcost = 0
        self.gainbucket = []
        for _ in range(K):
            self.gainbucket += [bpqueue(-self.pmax, self.pmax)]

    def init(self, part_info):
        """(re)initialization after creation

        Arguments:
            part {list} -- [description]
        """
        totalcost = self.gainCalc.init(part_info)
        self.waitinglist.clear()
        return totalcost

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
        fromPart = part[i_v]
        move_info_v = fromPart, toPart, i_v
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
        return i_v, gainmax

    def update_move(self, part_info, move_info_v):
        """[summary]

        Arguments:
            part_info {[type]} -- [description]
            move_info_v {[type]} -- [description]
        """
        # self.deltaGainV = list(0 for _ in range(self.K))
        self.gainCalc.update_move_init()

        fromPart, toPart, i_v = move_info_v
        v = self.H.modules[i_v]
        for net in self.H.G[v]:
            degree = self.H.G.degree[net]
            if degree < 2:  # unlikely, self-loop, etc.
                continue  # does not provide any gain change when move
            move_info = [net, fromPart, toPart, v]
            if degree == 3:
                self.update_move_3pin_net(part_info, move_info)
            elif degree == 2:
                self.update_move_2pin_net(part_info, move_info)
            else:
                self.update_move_general_net(part_info, move_info)

    # private:

    @abstractmethod
    def modify_key(self, i_w, part_w, key):
        """Abstract method

        Arguments:
            w {node_t} -- [description]
            part_w {uint8_t} -- [description]
            key {int/int[]} -- [description]
        """

    def update_move_2pin_net(self, part_info, move_info):
        """Update move for 2-pin net

        Arguments:
            part_info {[type]} -- [description]
            move_info {[type]} -- [description]
        """
        i_w, deltaGainW = self.gainCalc.update_move_2pin_net(
            part_info, move_info)
        part, _ = part_info
        self.modify_key(i_w, part[i_w], deltaGainW)

    def update_move_3pin_net(self, part_info, move_info):
        """Update move for 3-pin net

        Arguments:
            part_info {[type]} -- [description]
            move_info {[type]} -- [description]
        """
        IdVec, deltaGain = self.gainCalc.update_move_3pin_net(
            part_info, move_info)
        part, _ = part_info
        for idx, i_w in enumerate(IdVec):
            self.modify_key(i_w, part[i_w], deltaGain[idx])

    def update_move_general_net(self, part_info, move_info):
        """Update move for general net

        Arguments:
            part_info {[type]} -- [description]
            move_info {[type]} -- [description]
        """
        IdVec, deltaGain = self.gainCalc.update_move_general_net(
            part_info, move_info)
        part, _ = part_info
        # degree = len(IdVec)
        # for idx in range(degree):
        #     i_w = IdVec[idx]
        for idx, i_w in enumerate(IdVec):
            self.modify_key(i_w, part[i_w], deltaGain[idx])
