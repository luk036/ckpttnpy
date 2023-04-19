from .bpqueue import BPQueue
from .dllist import Dllist, Dllink

from abc import abstractmethod
from typing import List

Item = Dllink[List[int]]


class FMGainMgr:
    waitinglist = Dllist[List[int]]([0, 3734])

    # public:

    def __init__(self, GainCalc, hgr, num_parts=2):
        """initialiation

        Arguments:
            hgr (Netlist):  description
            GainCalc (type):  description

        Keyword Arguments:
            num_parts (int):  number of partitions (default: {2})
        """
        self.hgr = hgr
        self.num_parts = num_parts
        self.gain_calc = GainCalc(hgr, num_parts)
        self.pmax = self.hgr.get_max_degree()
        self.gainbucket = [BPQueue(-self.pmax, self.pmax)
                           for _ in range(num_parts)]

    def init(self, part):
        """(re)initialization after creation

        Arguments:
            part (list):  description
        """
        totalcost = self.gain_calc.init(part)
        self.waitinglist.clear()
        return totalcost

    def is_empty_togo(self, to_part):
        """[summary]

        Arguments:
            to_part (uint8_t):  description

        Returns:
            bool:  description
        """
        return self.gainbucket[to_part]._max == 0  # is_empty()

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
        # gainmax = list(self.gainbucket[k].get_max() for k in range(self.num_parts))
        # maxk = max(gainmax)
        # to_part = gainmax.index(maxk)
        to_part = max(range(self.num_parts),
                      key=lambda k: self.gainbucket[k].get_max())
        maxk = self.gainbucket[to_part].get_max()

        vlink = self.gainbucket[to_part].popleft()
        self.waitinglist.append(vlink)
        v = vlink.data[1]
        from_part = part[v]
        move_info_v = v, from_part, to_part
        return move_info_v, maxk

    def select_togo(self, to_part):
        """Select best candidaate togo

        Arguments:
            to_part (uint8_t):  description

        Returns:
            node_t:  description
        """
        gainmax = self.gainbucket[to_part].get_max()
        vlink = self.gainbucket[to_part].popleft()
        self.waitinglist.append(vlink)
        v = vlink.data[1]
        return v, gainmax

    def update_move(self, part, move_info_v):
        """[summary]

        Arguments:
            part (list):  description
            move_info_v (type):  description
        """
        self.gain_calc.update_move_init()
        v, from_part, to_part = move_info_v
        for net in self.hgr.gr[v]:
            degree = self.hgr.gr.degree[net]
            if degree < 2:  # unlikely, self-loop, etc.
                continue  # does not provide any gain change when move
            move_info = [net, v, from_part, to_part]
            if degree == 2:
                self._update_move_2pin_net(part, move_info)
            else:
                self.gain_calc.init_idx_vec(v, net)
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
        pass

    # private:

    def _update_move_2pin_net(self, part, move_info):
        """Update move for 2-pin net

        Arguments:
            part (list):  Partition sol'n
            move_info (type):  description
        """
        w = self.gain_calc.update_move_2pin_net(part, move_info)
        self.modify_key(w, part[w], self.gain_calc.delta_gain_w)

    def _update_move_3pin_net(self, part, move_info):
        """Update move for 3-pin net

        Arguments:
            part (list):  Partition sol'n
            move_info (type):  description
        """
        delta_gain = self.gain_calc.update_move_3pin_net(part, move_info)
        for dGw, w in zip(delta_gain, self.gain_calc.idx_vec):
            self.modify_key(w, part[w], dGw)

    def _update_move_general_net(self, part, move_info):
        """Update move for general net

        Arguments:
            part (list):  Partition sol'n
            move_info (type):  description
        """
        delta_gain = self.gain_calc.update_move_general_net(part, move_info)
        for dGw, w in zip(delta_gain, self.gain_calc.idx_vec):
            self.modify_key(w, part[w], dGw)
