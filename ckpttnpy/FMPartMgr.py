from .PartMgrBase import PartMgrBase

# **Special code for two-pin nets**
# Take a snapshot when a move make **negative** gain.
# Snapshot in the form of "interface"???


class FMPartMgr(PartMgrBase):

    def take_snapshot(self, part_info):
        """[summary]

        Arguments:
            part_info {[type]} -- [description]

        Returns:
            [type] -- [description]
        """
        # extern_nets_ss, extern_modules_ss = snapshot
        part, _ = part_info
        return list(part)

    def restore_part_info(self, snapshot, part_info):
        """[summary]

        Arguments:
            snapshot {[type]} -- [description]

        Returns:
            [type] -- [description]
        """
        part, _ = part_info
        for i_v, k in enumerate(snapshot):
            part[i_v] = k
