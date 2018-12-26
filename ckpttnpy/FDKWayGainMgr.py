from .FDGainMgr import FDGainMgr
from .robin import robin


class FDKWayGainMgr(FDGainMgr):

    # public:

    def __init__(self, GainCalc, H, K):
        """Initialization

        Arguments:
            GainCalc {[type]} -- [description]
            H {Netlist} -- [description]
            K {uint8_t} -- number of partitions
        """
        FDGainMgr.__init__(self, GainCalc, H, K)
        self.RR = robin(K)

    def init(self, part_info):
        """(re)initialization after creation

        Arguments:
            part_info {[type]} -- [description]
        """
        totalcost = FDGainMgr.init(self, part_info)
        part, _ = part_info
        for k in range(self.K):
            self.gainbucket[k].clear()

        for v in range(self.H.number_of_modules()):
            for k in range(self.K):
                vlink = self.gainCalc.vertex_list[k][v]
                if part[v] == k:
                    # assert vlink.key == 0
                    self.gainbucket[k].set_key(vlink, 0)
                    self.waitinglist.append(vlink)
                else:
                    self.gainbucket[k].append(vlink, vlink.key)

        return totalcost

    def set_key(self, whichPart, v, key):
        """Set key

        Arguments:
            whichPart {uint8_t} -- [description]
            v {node_t} -- [description]
            key {int} -- [description]
        """
        self.gainbucket[whichPart].set_key(
            self.gainCalc.vertex_list[whichPart][v], key)

    def update_move_v(self, part, move_info_v, gain):
        """Update gain for the moving cell

        Arguments:
            part {[type]} -- [description]
            move_info_v {[type]} -- [description]
            gain {[type]} -- [description]
        """
        fromPart, toPart, v = move_info_v
        for k in range(self.K):
            if fromPart == k or toPart == k:
                continue
            self.gainbucket[k].modify_key(self.gainCalc.vertex_list[k][v],
                                          self.gainCalc.deltaGainV[k])
        self.set_key(fromPart, v, -gain)
        self.set_key(toPart, v, -2*self.pmax)

    # private:

    def modify_key(self, w, part_w, key):
        """[summary]

        Arguments:
            w {[type]} -- [description]
            part_w {[type]} -- [description]
            key {[type]} -- [description]
        """
        for k in self.RR.exclude(part_w):
            self.gainbucket[k].modify_key(
                self.gainCalc.vertex_list[k][w], key[k])
