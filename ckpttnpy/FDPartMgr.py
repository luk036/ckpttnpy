# **Special code for two-pin nets**
# Take a snapshot when a move make **negative** gain.
# Snapshot in the form of "interface"???
from collections import deque
from .PartMgrBase import PartMgrBase


class FDPartMgr(PartMgrBase):
    # def __init__(self, H, gainMgr, constrMgr):
    #     """[summary]

    #     Arguments:
    #         H {[type]} -- [description]
    #         gainMgr {[type]} -- [description]
    #         constrMgr {[type]} -- [description]
    #     """
    #     PartMgrBase.__init__(self, H, gainMgr, constrMgr)

    def take_snapshot(self, part_info):
        """[summary]

        Arguments:
            part_info {[type]} -- [description]

        Returns:
            [type] -- [description]
        """
        part, extern_nets = part_info

        # extern_modules_ss = {v: part[v]
        #                      for net in extern_nets for v in self.H.G[net]}
        extern_modules_ss = {}
        for net in extern_nets:
            for v in self.H.G[net]:
                i_v = self.H.module_map[v]
                extern_modules_ss[v] = part[i_v]

        extern_nets_ss = extern_nets.copy()
        return extern_nets_ss, extern_modules_ss

    def restore_part_info(self, snapshot, part_info):
        """[summary]

        Arguments:
            snapshot {[type]} -- [description]

        Returns:
            [type] -- [description]
        """
        extern_nets_ss, extern_modules_ss = snapshot
        part, extern_nets = part_info
        for i_v in range(self.H.number_of_modules()):
            part[i_v] = self.K
        for v, part_v in extern_modules_ss.items():
            i_v = self.H.module_map[v]
            part[i_v] = part_v
            Q = deque()
            Q.append(v)
            while Q:
                v2 = Q.popleft()
                for net in self.H.G[v2]:
                    if self.H.G.degree(net) < 2:
                        continue
                    if net in extern_nets_ss:
                        continue
                    for v3 in self.H.G[net]:
                        i_v3 = self.H.module_map[v3]
                        if part[i_v3] < self.K:
                            continue
                        part[i_v3] = part_v
                        Q.append(v3)

        extern_nets.clear()
        for net in extern_nets_ss:
            extern_nets.add(net)
