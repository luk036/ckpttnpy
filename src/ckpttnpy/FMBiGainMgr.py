# -*- coding: utf-8 -*-

from typing import Any, Dict, List, Union

from .FMGainMgr import FMGainMgr

Part = Union[Dict[Any, int], List[int]]


class FMBiGainMgr(FMGainMgr):

    # public:

    # def __init__(self, GainCalc, H, K=2):
    #     """Initialization

    #     Arguments:
    #         H (Netlist):  description
    #         GainCalc (type):  description
    #         K (uint8_t):  number of partitions
    #     """
    #     FMGainMgr.__init__(self, GainCalc, H)

    def init(self, part: Part):
        """(re)initialization after creation

        Arguments:
            part (list):  description
        """
        totalcost = FMGainMgr.init(self, part)

        for k in range(self.K):
            self.gainbucket[k].clear()

        for v in self.H.modules:
            vlink = self.gainCalc.vertex_list[v]
            toPart = 1 - part[v]
            self.gainbucket[toPart].append_direct(vlink)

        for v in self.H.module_fixed:
            self.lock_all(part[v], v)

        return totalcost

    def lock(self, whichPart, v):
        """Lock

        Arguments:
            whichPart (uint8_t):  description
            v (node_t):  description
        """
        vlink = self.gainCalc.vertex_list[v]
        self.gainbucket[whichPart].detach(vlink)
        vlink.lock()

    def lock_all(self, fromPart, v):
        """Lock

        Arguments:
            whichPart (uint8_t):  description
            v (node_t):  description
        """
        toPart = 1 - fromPart
        self.lock(toPart, v)

    # private:
    def __set_key(self, whichPart, v, key):
        """Set key

        Arguments:
            whichPart (uint8_t):  description
            v (node_t):  description
            key (int):  description
        """
        self.gainbucket[whichPart].set_key(
            self.gainCalc.vertex_list[v], key)

    def modify_key(self, w, part_w, key):
        """Update gain for the moving cell

        Arguments:
            part (type):  description
            move_info_v (type):  description
            gain (type):  description
        """
        self.gainbucket[1-part_w].modify_key(
            self.gainCalc.vertex_list[w], key)

    def update_move_v(self, move_info_v, gain):
        """[summary]

        Arguments:
            part (type):  description
            w (type):  description
            key (type):  description
        """
        fromPart, _, v = move_info_v
        self.__set_key(fromPart, v, -gain)
