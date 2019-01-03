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
        # extern_nets_ss, extern_modules_ss = snapshot
        part, extern_nets = part_info
        # extern_nets_ss = extern_nets.copy()
        extern_modules_ss = {}
        for net in extern_nets:
            for v in self.H.G[net]:
                extern_modules_ss[v] = part[v]
        # extern_nets_ss = set()
        # for net in extern_nets:
        #     extern_nets_ss.add(net)
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
        # part = list(self.K for _ in range(self.H.number_of_modules()))
        for v in range(self.H.number_of_modules()):
            part[v] = self.K
        # Q = deque(v for v, _ in extern_modules_ss.items())
        # while Q:
        #     v = Q.popleft()
        for v, part_v in extern_modules_ss.items():
            #if part[v] < self.K:
            #    continue
            #part_v = part[v] = extern_modules_ss[v]
            part[v] = part_v
            Q2 = deque()
            Q2.append(v)
            while Q2:
                v2 = Q2.popleft()
                for net in self.H.G[v2]:
                    if self.H.G.degree(net) < 2:
                        continue
                    if net in extern_nets_ss:
                        continue
                    for v3 in self.H.G[net]:
                        if part[v3] < self.K:
                            continue
                        part[v3] = part_v
                        Q2.append(v3)

        extern_nets.clear()
        for net in extern_nets_ss:
            extern_nets.add(net)
