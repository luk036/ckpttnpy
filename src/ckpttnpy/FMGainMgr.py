from abc import abstractmethod

from .bpqueue import bpqueue
from .dllist import dllink


class FMGainMgr:
    waitinglist = dllink(3734)

    # public:

    def __init__(self, GainCalc, H, K=2):
        """initialiation

        Arguments:
            H {Netlist}:  description
            GainCalc (type):  description

        Keyword Arguments:
            K {int}:  number of partitions (default: {2})
        """
        self.H = H
        self.K = K
        self.gainCalc = GainCalc(H, K)
        self.pmax = self.H.get_max_degree()
        self.gainbucket = [bpqueue(-self.pmax, self.pmax)
                           for _ in range(K)]

    def init(self, part):
        """(re)initialization after creation

        Arguments:
            part {list}:  description
        """
        totalcost = self.gainCalc.init(part)
        self.waitinglist.clear()
        return totalcost

    def is_empty_togo(self, toPart):
        """[summary]

        Arguments:
            toPart {uint8_t}:  description

        Returns:
            bool:  description
        """
        return self.gainbucket[toPart].is_empty()

    def is_empty(self):
        """Any more candidate?

        Returns:
            bool:  description
        """
        for k in range(self.K):
            if not self.gainbucket[k].is_empty():
                return False
        return True

    def select(self, part):
        """Select best candidate

        Arguments:
            part {list}:  description

        Returns:
            move_info_v:  description
        """
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
        """Select best candidaate togo

        Arguments:
            toPart {uint8_t}:  description

        Returns:
            node_t:  description
        """
        gainmax = self.gainbucket[toPart].get_max()
        vlink = self.gainbucket[toPart].popleft()
        self.waitinglist.append(vlink)
        v = vlink.idx
        return v, gainmax

    def update_move(self, part, move_info_v):
        """[summary]

        Arguments:
            part {list}:  description
            move_info_v (type):  description
        """
        self.gainCalc.update_move_init()
        fromPart, toPart, v = move_info_v
        # v = v
        for net in self.H.G[v]:
            degree = self.H.G.degree[net]
            if degree < 2:  # unlikely, self-loop, etc.
                continue  # does not provide any gain change when move
            move_info = [net, fromPart, toPart, v]
            if degree == 3:
                self.__update_move_3pin_net(part, move_info)
            elif degree == 2:
                self.__update_move_2pin_net(part, move_info)
            else:
                self.__update_move_general_net(part, move_info)

    @abstractmethod
    def modify_key(self, w, part_w, key):
        """Abstract method

        Arguments:
            part {uint8_t}:  description
            w {node_t}:  description
            key {int/int[]}:  description
        """

    # private:

    def __update_move_2pin_net(self, part, move_info):
        """Update move for 2-pin net

        Arguments:
            part {list}:  Partition sol'n
            move_info (type):  description
        """
        w, deltaGainW = self.gainCalc.update_move_2pin_net(
            part, move_info)
        self.modify_key(w, part[w], deltaGainW)

    def __update_move_3pin_net(self, part, move_info):
        """Update move for 3-pin net

        Arguments:
            part {list}:  Partition sol'n
            move_info (type):  description
        """
        IdVec, deltaGain = self.gainCalc.update_move_3pin_net(
            part, move_info)
        for idx, w in enumerate(IdVec):
            self.modify_key(w, part[w], deltaGain[idx])

    def __update_move_general_net(self, part, move_info):
        """Update move for general net

        Arguments:
            part {list}:  Partition sol'n
            move_info (type):  description
        """
        IdVec, deltaGain = self.gainCalc.update_move_general_net(
            part, move_info)
        for idx, w in enumerate(IdVec):
            self.modify_key(w, part[w], deltaGain[idx])
