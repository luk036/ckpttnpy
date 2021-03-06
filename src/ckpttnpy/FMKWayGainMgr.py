# -*- coding: utf-8 -*-

from typing import Any, Dict, List, Union

from .FMGainMgr import FMGainMgr
from .robin import robin

Part = Union[Dict[Any, int], List[int]]


class FMKWayGainMgr(FMGainMgr):

    # public:

    def __init__(self, GainCalc, H, K: int):
        """Initialization

        Arguments:
            H (Netlist):  description
            GainCalc (type):  description
            K (uint8_t):  number of partitions
        """
        FMGainMgr.__init__(self, GainCalc, H, K)
        self.RR = robin(K)

    def init(self, part: Part):
        """(re)initialization after creation

        Arguments:
            part (list):  description
        """
        totalcost = FMGainMgr.init(self, part)

        for bckt in self.gainbucket:
            bckt.clear()

        for v in self.H.modules:
            pv = part[v]
            for k in self.RR.exclude(pv):
                vlink = self.gainCalc.vertex_list[k][v]
                self.gainbucket[k].append(vlink, vlink.data[0])
            vlink = self.gainCalc.vertex_list[pv][v]
            self.gainbucket[pv].set_key(vlink, 0)
            self.waitinglist.append(vlink)

        for v in self.H.module_fixed:
            self.lock_all(part[v], v)

        return totalcost

    def lock(self, whichPart, v):
        """Set key

        Arguments:
            whichPart (uint8_t):  description
            v (node_t):  description
            key (int):  description
        """
        vlink = self.gainCalc.vertex_list[whichPart][v]
        self.gainbucket[whichPart].detach(vlink)
        vlink.next = None  # lock

    def lock_all(self, _, v):
        for vlist, bckt in zip(self.gainCalc.vertex_list, self.gainbucket):
            vlink = vlist[v]
            bckt.detach(vlink)
            vlink.next = None  # lock

    def update_move_v(self, move_info_v, gain):
        """Update gain for the moving cell

        Arguments:
            part (type):  description
            move_info_v (type):  description
            gain (type):  description
        """
        v, fromPart, toPart = move_info_v
        for k in range(self.K):
            if fromPart == k or toPart == k:
                continue
            self.gainbucket[k].modify_key(self.gainCalc.vertex_list[k][v],
                                          self.gainCalc.deltaGainV[k])
        self._set_key(fromPart, v, -gain)
        # self.lock(toPart, v)

    def modify_key(self, w, part_w, key):
        """[summary]

        Arguments:
            part (type):  description
            w (type):  description
            key (type):  description
        """
        for k in self.RR.exclude(part_w):
            self.gainbucket[k].modify_key(
                self.gainCalc.vertex_list[k][w], key[k])

    # private:

    def _set_key(self, whichPart, v, key):
        """Set key

        Arguments:
            whichPart (uint8_t):  description
            v (node_t):  description
            key (int):  description
        """
        self.gainbucket[whichPart].set_key(
            self.gainCalc.vertex_list[whichPart][v], key)
