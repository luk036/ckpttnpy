from .dllist import dllink
from .bpqueue import bpqueue
from .FMBiGainCalc import FMBiGainCalc
from .FMGainMgr import FMGainMgr


class FMBiGainMgr2(FMGainMgr):

    # public:

    def __init__(self, H, GainCalc):
        """initialization

        Arguments:
            module_dict {dict} -- [description]
        """
        FMGainMgr.__init__(self, H, GainCalc)

    def init(self, part):
        """(re)initialization after creation

        Arguments:
            part {list} -- [description]
        """
        FMGainMgr.init(self, part)

        for v in self.H.module_list:
            vlink = self.gainCalc.vertex_list[v]
            toPart = 1 - part[v]
            self.gainbucket[toPart].append(vlink, vlink.key)

    # private:
    def set_key(self, whichPart, v, key):
        self.gainbucket[whichPart].set_key(
            self.gainCalc.vertex_list[v], key)

    def modify_key(self, part, w, key):
        part_w = part[w]
        self.gainbucket[1-part_w].modify_key(
                self.gainCalc.vertex_list[w], key)

    def update_move_v(self, part, move_info_v, gain):
        fromPart, _, v = move_info_v
        self.set_key(fromPart, v, -gain)
