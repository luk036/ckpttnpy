from .PartMgrBase import PartMgrBase

# **Special code for two-pin nets**
# Take a snapshot when a move make **negative** gain.
# Snapshot in the form of "interface"???


class FMPartMgr(PartMgrBase):

    def take_snapshot(self, part):
        """[summary]

        Arguments:
            part (type):  description

        Returns:
            dtype:  description
        """
        return list(part)

    def restore_part_info(self, snapshot, part):
        """[summary]

        Arguments:
            snapshot (type):  description

        Returns:
            dtype:  description
        """
        for i_v, k in enumerate(snapshot):
            part[i_v] = k
