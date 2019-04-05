from .FMGainMgr import FMGainMgr
from .robin import robin


class FMKWayGainMgr(FMGainMgr):

    # public:

    def __init__(self, GainCalc, H, K):
        """Initialization

        Arguments:
            H {Netlist} -- [description]
            GainCalc {[type]} -- [description]
            K {uint8_t} -- number of partitions
        """
        FMGainMgr.__init__(self, GainCalc, H, K)
        self.RR = robin(K)

    def init(self, part):
        """(re)initialization after creation

        Arguments:
            part {list} -- [description]
        """
        # part, _ = part_info
        totalcost = FMGainMgr.init(self, part)

        for k in range(self.K):
            self.gainbucket[k].clear()

        for i_v in range(self.H.number_of_modules()):
            pv = part[i_v]
            for k in self.RR.exclude(pv):
                vlink = self.gainCalc.vertex_list[k][i_v]
                self.gainbucket[k].append(vlink, vlink.key)
            vlink = self.gainCalc.vertex_list[pv][i_v]
            self.gainbucket[pv].set_key(vlink, 0)
            self.waitinglist.append(vlink)

        for v in self.H.module_fixed:
            i_v = self.H.module_map[v]
            self.lock_all(part[i_v], i_v)

        return totalcost

    def lock(self, whichPart, i_v):
        """Set key

        Arguments:
            whichPart {uint8_t} -- [description]
            v {node_t} -- [description]
            key {int} -- [description]
        """
        vlink = self.gainCalc.vertex_list[whichPart][i_v]
        self.gainbucket[whichPart].detach(vlink)
        vlink.lock()

    def lock_all(self, fromPart, i_v):
        for k in range(self.K):
            self.lock(k, i_v)

    def set_key(self, whichPart, i_v, key):
        """Set key

        Arguments:
            whichPart {uint8_t} -- [description]
            v {node_t} -- [description]
            key {int} -- [description]
        """
        self.gainbucket[whichPart].set_key(
            self.gainCalc.vertex_list[whichPart][i_v], key)

    def update_move_v(self, move_info_v, gain):
        """Update gain for the moving cell

        Arguments:
            part {[type]} -- [description]
            move_info_v {[type]} -- [description]
            gain {[type]} -- [description]
        """
        fromPart, toPart, i_v = move_info_v
        for k in range(self.K):
            if fromPart == k or toPart == k:
                continue
            self.gainbucket[k].modify_key(self.gainCalc.vertex_list[k][i_v],
                                          self.gainCalc.deltaGainV[k])
        self.set_key(fromPart, i_v, -gain)
        # self.lock(toPart, i_v)

    # private:

    def modify_key(self, i_w, part_w, key):
        """[summary]

        Arguments:
            part {[type]} -- [description]
            w {[type]} -- [description]
            key {[type]} -- [description]
        """
        for k in self.RR.exclude(part_w):
            self.gainbucket[k].modify_key(
                self.gainCalc.vertex_list[k][i_w], key[k])
