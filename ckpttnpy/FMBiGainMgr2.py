from .FMGainMgr import FMGainMgr


class FMBiGainMgr2(FMGainMgr):

    # public:

    def __init__(self, GainCalc, H):
        """Initialization

        Arguments:
            H {Netlist} -- [description]
            GainCalc {[type]} -- [description]
            K {uint8_t} -- number of partitions
        """
        FMGainMgr.__init__(self, GainCalc, H)

    def init(self, part):
        """(re)initialization after creation

        Arguments:
            part {list} -- [description]
        """
        FMGainMgr.init(self, part)
        for k in range(self.K):
            self.gainbucket[k].clear()

        for i_v in range(self.H.number_of_modules()):
            vlink = self.gainCalc.vertex_list[i_v]
            toPart = 1 - part[i_v]
            self.gainbucket[toPart].append_direct(vlink)

    def init_luk(self, soln_info):
        """(re)initialization after creation

        Arguments:
            part {list} -- [description]
        """
        FMGainMgr.init_luk(self, soln_info)
        for k in range(self.K):
            self.gainbucket[k].clear()

        part, _ = soln_info
        for i_v in range(self.H.number_of_modules()):
            vlink = self.gainCalc.vertex_list[i_v]
            toPart = 1 - part[i_v]
            self.gainbucket[toPart].append_direct(vlink)

    # private:
    def set_key(self, whichPart, i_v, key):
        """Set key

        Arguments:
            whichPart {uint8_t} -- [description]
            v {node_t} -- [description]
            key {int} -- [description]
        """
        self.gainbucket[whichPart].set_key(
            self.gainCalc.vertex_list[i_v], key)

    def modify_key(self, part, i_w, key):
        """Update gain for the moving cell

        Arguments:
            part {[type]} -- [description]
            move_info_v {[type]} -- [description]
            gain {[type]} -- [description]
        """
        part_w = part[i_w]
        self.gainbucket[1-part_w].modify_key(
            self.gainCalc.vertex_list[i_w], key)

    def update_move_v(self, part, move_info_v, gain):
        """[summary]

        Arguments:
            part {[type]} -- [description]
            w {[type]} -- [description]
            key {[type]} -- [description]
        """
        fromPart, _, _, i_v = move_info_v
        self.set_key(fromPart, i_v, -gain)
