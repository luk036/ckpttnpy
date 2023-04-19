# -*- coding: utf-8 -*-

from typing import Any, Dict, List, Union

from .FMGainMgr import FMGainMgr
from .robin import Robin

Part = Union[Dict[Any, int], List[int]]


class FMKWayGainMgr(FMGainMgr):
    # public:

    def __init__(self, GainCalc, hgr, num_parts: int):
        """Initialization

        Arguments:
            hgr (Netlist):  description
            GainCalc (type):  description
            num_parts (uint8_t):  number of partitions
        """
        FMGainMgr.__init__(self, GainCalc, hgr, num_parts)
        self.rr = Robin(num_parts)

    def init(self, part: Part):
        """(re)initialization after creation

        Arguments:
            part (list):  description
        """
        totalcost = FMGainMgr.init(self, part)

        for bckt in self.gainbucket:
            bckt.clear()

        for v in self.hgr:
            pv = part[v]
            for k in self.rr.exclude(pv):
                vlink = self.gain_calc.vertex_list[k][v]
                self.gainbucket[k].append(vlink, vlink.data[0])
            vlink = self.gain_calc.vertex_list[pv][v]
            self.gainbucket[pv].set_key(vlink, 0)
            self.waitinglist.append(vlink)

        for v in self.hgr.module_fixed:
            self.lock_all(part[v], v)

        return totalcost

    def lock(self, whichPart, v):
        """Set key

        Arguments:
            whichPart (uint8_t):  description
            v (node_t):  description
            key (int):  description
        """
        vlink = self.gain_calc.vertex_list[whichPart][v]
        self.gainbucket[whichPart].detach(vlink)
        vlink.next = vlink  # lock

    def lock_all(self, _, v):
        for vlist, bckt in zip(self.gain_calc.vertex_list, self.gainbucket):
            vlink = vlist[v]
            bckt.detach(vlink)
            vlink.next = vlink  # lock

    def update_move_v(self, move_info_v, gain):
        """Update gain for the moving cell

        Arguments:
            part (type):  description
            move_info_v (type):  description
            gain (type):  description
        """
        v, from_part, to_part = move_info_v
        for k in filter(lambda k: k != to_part, self.rr.exclude(from_part)):
            self.gainbucket[k].modify_key(
                self.gain_calc.vertex_list[k][v], self.gain_calc.delta_gain_v[k]
            )
        self._set_key(from_part, v, -gain)
        # self.lock(to_part, v)

    def modify_key(self, w, part_w, key):
        """[summary]

        Arguments:
            part (type):  description
            w (type):  description
            key (type):  description
        """
        for k in self.rr.exclude(part_w):
            self.gainbucket[k].modify_key(self.gain_calc.vertex_list[k][w], key[k])

    # private:

    def _set_key(self, whichPart, v, key):
        """Set key

        Arguments:
            whichPart (uint8_t):  description
            v (node_t):  description
            key (int):  description
        """
        self.gainbucket[whichPart].set_key(
            self.gain_calc.vertex_list[whichPart][v], key
        )
