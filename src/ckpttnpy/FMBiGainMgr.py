from .FMGainMgr import FMGainMgr

from typing import Any, Dict, List, Union

Part = Union[Dict[Any, int], List[int]]


class FMBiGainMgr(FMGainMgr):
    # public:

    # def __init__(self, GainCalc, hgr, num_parts=2):
    #     """Initialization

    #     Arguments:
    #         hgr (Netlist):  description
    #         GainCalc (type):  description
    #         num_parts (uint8_t):  number of partitions
    #     """
    #     FMGainMgr.__init__(self, GainCalc, hgr)

    def init(self, part: Part):
        """(re)initialization after creation

        Arguments:
            part (list):  description
        """
        totalcost = FMGainMgr.init(self, part)

        for bckt in self.gainbucket:
            bckt.clear()

        for v in self.hgr:
            vlink = self.gain_calc.vertex_list[v]
            to_part = part[v] ^ 1  # toggle 0 or 1
            self.gainbucket[to_part].append_direct(vlink)

        for v in self.hgr.module_fixed:
            self.lock_all(part[v], v)

        return totalcost

    def lock(self, whichPart, v):
        """Lock

        Arguments:
            whichPart (uint8_t):  description
            v (node_t):  description
        """
        vlink = self.gain_calc.vertex_list[v]
        self.gainbucket[whichPart].detach(vlink)
        vlink.next = vlink  # lock

    def lock_all(self, from_part, v):
        """Lock

        Arguments:
            whichPart (uint8_t):  description
            v (node_t):  description
        """
        self.lock(from_part ^ 1, v)

    def modify_key(self, w, part_w, key):
        """Update gain for the moving cell

        Arguments:
            part (type):  description
            move_info_v (type):  description
            gain (type):  description
        """
        self.gainbucket[part_w ^ 1].modify_key(self.gain_calc.vertex_list[w], key)

    def update_move_v(self, move_info_v, gain):
        """[summary]

        Arguments:
            part (type):  description
            w (type):  description
            key (type):  description
        """
        v, from_part, _ = move_info_v
        self._set_key(from_part, v, -gain)

    # private:

    def _set_key(self, whichPart, v, key):
        """Set key

        Arguments:
            whichPart (uint8_t):  description
            v (node_t):  description
            key (int):  description
        """
        self.gainbucket[whichPart].set_key(self.gain_calc.vertex_list[v], key)
