from .FMGainMgr import FMGainMgr


class FMKWayGainMgr(FMGainMgr):

    # public:

    def __init__(self, H, GainCalc, K):
        """Initialization

        Arguments:
            H {Netlist} -- [description]
            GainCalc {[type]} -- [description]
            K {uint8_t} -- number of partitions
        """
        FMGainMgr.__init__(self, H, GainCalc, K)

    def init(self, part):
        """(re)initialization after creation

        Arguments:
            part {list} -- [description]
        """
        FMGainMgr.init(self, part)

        for k in range(self.K):
            self.gainbucket[k].clear()

        for i_v in range(self.H.number_of_modules()):
            for k in range(self.K):
                vlink = self.gainCalc.vertex_list[k][i_v]
                if part[i_v] == k:
                    # assert vlink.key == 0
                    self.gainbucket[k].set_key(vlink, 0)
                    self.waitinglist.append(vlink)
                else:
                    self.gainbucket[k].append(vlink, vlink.key)

    def set_key(self, whichPart, i_v, key):
        """Set key

        Arguments:
            whichPart {uint8_t} -- [description]
            v {node_t} -- [description]
            key {int} -- [description]
        """
        self.gainbucket[whichPart].set_key(
            self.gainCalc.vertex_list[whichPart][i_v], key)

    def update_move_v(self, part, move_info_v, gain):
        """Update gain for the moving cell

        Arguments:
            part {[type]} -- [description]
            move_info_v {[type]} -- [description]
            gain {[type]} -- [description]
        """
        fromPart, toPart, _, i_v = move_info_v
        for k in range(self.K):
            if fromPart == k or toPart == k:
                continue
            self.gainbucket[k].modify_key(self.gainCalc.vertex_list[k][i_v],
                                          self.gainCalc.deltaGainV[k])
        self.set_key(fromPart, i_v, -gain)
        self.set_key(toPart, i_v, 0)  # actually don't care

    # private:

    def modify_key(self, part, i_w, key):
        """[summary]

        Arguments:
            part {[type]} -- [description]
            w {[type]} -- [description]
            key {[type]} -- [description]
        """
        for k in range(self.K):
            if part[i_w] == k:
                continue
            self.gainbucket[k].modify_key(
                self.gainCalc.vertex_list[k][i_w], key[k])
