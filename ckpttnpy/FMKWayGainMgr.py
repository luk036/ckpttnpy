from .dllist import dllink
from .bpqueue import bpqueue
from .FMKWayGainCalc import FMKWayGainCalc
from .FMGainMgr import FMGainMgr


class FMKWayGainMgr(FMGainMgr):

    # public:

    def __init__(self, H, GainCalc, K):
        """initialization

        Arguments:
            module_dict {dict} -- [description]
        """
        FMGainMgr.__init__(self, H, GainCalc, K)

    def init(self, part):
        """(re)initialization after creation

        Arguments:
            part {list} -- [description]
        """
        FMGainMgr.init(self, part)

        for v in self.H.module_list:
            for k in range(self.K):
                vlink = self.gainCalc.vertex_list[k][v]
                if part[v] == k:
                    assert vlink.key == 0
                    self.gainbucket[k].set_key(vlink, 0)
                    self.waitinglist.append(vlink)
                else:
                    self.gainbucket[k].append(vlink, vlink.key)

    def set_key(self, whichPart, v, key):
        self.gainbucket[whichPart].set_key(
            self.gainCalc.vertex_list[whichPart][v], key)

    def update_move_v(self, part, move_info_v, gain):
        fromPart, toPart, v = move_info_v
        for k in range(self.K):
            if fromPart == k or toPart == k:
                continue
            self.gainbucket[k].modify_key(self.gainCalc.vertex_list[k][v],
                                          self.gainCalc.deltaGainV[k])
        self.set_key(fromPart, v, -gain)
        self.set_key(toPart, v, 0)  # actually don't care

    # private:

    def modify_key(self, part, w, keys):
        for k in range(self.K):
            if part[w] == k:
                continue
            self.gainbucket[k].modify_key(
                self.gainCalc.vertex_list[k][w], keys[k])
