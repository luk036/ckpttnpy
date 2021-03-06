# -*- coding: utf-8 -*-

from abc import abstractmethod

from .bpqueue import bpqueue
from .dllist import dllink


class FMGainMgr:
    waitinglist = dllink([0, 3734])

    # public:

    def __init__(self, GainCalc, H, K=2):
        """initialiation

        Arguments:
            H (Netlist):  description
            GainCalc (type):  description

        Keyword Arguments:
            K (int):  number of partitions (default: {2})
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
            part (list):  description
        """
        totalcost = self.gainCalc.init(part)
        self.waitinglist.clear()
        return totalcost

    def is_empty_togo(self, toPart):
        """[summary]

        Arguments:
            toPart (uint8_t):  description

        Returns:
            bool:  description
        """
        return self.gainbucket[toPart]._max == 0  # is_empty()

    def is_empty(self):
        """Any more candidate?

        Returns:
            bool:  description
        """
        return all(bckt._max == 0 for bckt in self.gainbucket)

    def select(self, part):
        """Select best candidate

        Arguments:
            part (list):  description

        Returns:
            move_info_v:  description
        """
        # gainmax = list(self.gainbucket[k].get_max() for k in range(self.K))
        # maxk = max(gainmax)
        # toPart = gainmax.index(maxk)
        toPart = max(range(self.K), key=lambda k: self.gainbucket[k].get_max())
        maxk = self.gainbucket[toPart].get_max()
        vlink = self.gainbucket[toPart].popleft()
        self.waitinglist.append(vlink)
        v = vlink.data[1]
        fromPart = part[v]
        move_info_v = v, fromPart, toPart
        return move_info_v, maxk

    def select_togo(self, toPart):
        """Select best candidaate togo

        Arguments:
            toPart (uint8_t):  description

        Returns:
            node_t:  description
        """
        gainmax = self.gainbucket[toPart].get_max()
        vlink = self.gainbucket[toPart].popleft()
        self.waitinglist.append(vlink)
        v = vlink.data[1]
        return v, gainmax

    def update_move(self, part, move_info_v):
        """[summary]

        Arguments:
            part (list):  description
            move_info_v (type):  description
        """
        self.gainCalc.update_move_init()
        v, fromPart, toPart = move_info_v
        # v = v
        for net in self.H.G[v]:
            degree = self.H.G.degree[net]
            if degree < 2:  # unlikely, self-loop, etc.
                continue  # does not provide any gain change when move
            move_info = [net, v, fromPart, toPart]
            if degree == 2:
                self._update_move_2pin_net(part, move_info)
            else:
                self.gainCalc.init_IdVec(v, net)
                if degree == 3:
                    self._update_move_3pin_net(part, move_info)
                else:
                    self._update_move_general_net(part, move_info)

    @abstractmethod
    def modify_key(self, w, part_w, key):
        """Abstract method

        Arguments:
            part (uint8_t):  description
            w (node_t):  description
            key (int/int[]):  description
        """

    # private:

    def _update_move_2pin_net(self, part, move_info):
        """Update move for 2-pin net

        Arguments:
            part (list):  Partition sol'n
            move_info (type):  description
        """
        w = self.gainCalc.update_move_2pin_net(
            part, move_info)
        self.modify_key(w, part[w], self.gainCalc.deltaGainW)

    def _update_move_3pin_net(self, part, move_info):
        """Update move for 3-pin net

        Arguments:
            part (list):  Partition sol'n
            move_info (type):  description
        """
        deltaGain = self.gainCalc.update_move_3pin_net(
            part, move_info)
        for dGw, w in zip(deltaGain, self.gainCalc.IdVec):
            self.modify_key(w, part[w], dGw)

    def _update_move_general_net(self, part, move_info):
        """Update move for general net

        Arguments:
            part (list):  Partition sol'n
            move_info (type):  description
        """
        deltaGain = self.gainCalc.update_move_general_net(
            part, move_info)
        for dGw, w in zip(deltaGain, self.gainCalc.IdVec):
            self.modify_key(w, part[w], dGw)
