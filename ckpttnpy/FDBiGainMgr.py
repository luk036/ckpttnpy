from .FDGainMgr import FDGainMgr


class FDBiGainMgr(FDGainMgr):

    # public:

    def __init__(self, GainCalc, H):
        """Initialization

        Arguments:
            H {Netlist} -- [description]
            GainCalc {[type]} -- [description]
            K {uint8_t} -- number of partitions
        """
        FDGainMgr.__init__(self, GainCalc, H)

    def init(self, soln_info):
        """(re)initialization after creation

        Arguments:
            part {list} -- [description]
        """
        FDGainMgr.init(self, soln_info)
        for k in range(self.K):
            self.gainbucket[k].clear()

        part, _, _ = soln_info
        for v in range(self.H.number_of_modules()):
            vlink = self.gainCalc.vertex_list[v]
            toPart = 1 - part[v]
            self.gainbucket[toPart].append_direct(vlink)

    # private:
    def set_key(self, whichPart, v, key):
        """Set key

        Arguments:
            whichPart {uint8_t} -- [description]
            v {node_t} -- [description]
            key {int} -- [description]
        """
        self.gainbucket[whichPart].set_key(
            self.gainCalc.vertex_list[v], key)

    def modify_key(self, w, part_w, key):
        """Update gain for the moving cell

        Arguments:
            part {[type]} -- [description]
            move_info_v {[type]} -- [description]
            gain {[type]} -- [description]
        """
        self.gainbucket[1-part_w].modify_key(
            self.gainCalc.vertex_list[w], key)

    def update_move_v(self, part, move_info_v, gain):
        """[summary]

        Arguments:
            part {[type]} -- [description]
            w {[type]} -- [description]
            key {[type]} -- [description]
        """
        fromPart, _, v = move_info_v
        self.set_key(fromPart, v, -gain)
