from .FDGainMgr import FDGainMgr


class FDBiGainMgr(FDGainMgr):

    # public:

    # def __init__(self, GainCalc, H, K=2):
    #     """Initialization

    #     Arguments:
    #         GainCalc {[type]} -- [description]
    #         H {Netlist} -- [description]
    #     """
    #     FDGainMgr.__init__(self, GainCalc, H)

    def init(self, part_info):
        """(re)initialization after creation

        Arguments:
            part_info {[type]} -- [description]
        """
        totalcost = FDGainMgr.init(self, part_info)
        for k in range(self.K):
            self.gainbucket[k].clear()

        part, _ = part_info
        for i_v in range(self.H.number_of_modules()):
            vlink = self.gainCalc.vertex_list[i_v]
            toPart = 1 - part[i_v]
            self.gainbucket[toPart].append_direct(vlink)

        for v in self.H.module_fixed:
            i_v = self.H.module_map[v]
            self.lock_all(part[i_v], i_v)

        return totalcost

    def lock(self, whichPart, i_v):
        """Lock

        Arguments:
            whichPart {uint8_t} -- [description]
            v {node_t} -- [description]
        """
        vlink = self.gainCalc.vertex_list[i_v]
        self.gainbucket[whichPart].detach(vlink)
        vlink.lock()

    def lock_all(self, fromPart, i_v):
        """Lock

        Arguments:
            whichPart {uint8_t} -- [description]
            v {node_t} -- [description]
        """
        toPart = 1 - fromPart
        self.lock(toPart, i_v)

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

    def modify_key(self, i_w, part_w, key):
        """Update gain for the moving cell

        Arguments:
            w {node_t} -- [description]
            part_w {[type]} -- [description]
            key {[type]} -- [description]
        """
        self.gainbucket[1-part_w].modify_key(
            self.gainCalc.vertex_list[i_w], key)

    def update_move_v(self, move_info_v, gain):
        """[summary]

        Arguments:
            part {[type]} -- [description]
            move_info_v {[type]} -- [description]
            gain {[type]} -- [description]
        """
        fromPart, _, i_v = move_info_v
        self.set_key(fromPart, i_v, -gain)
