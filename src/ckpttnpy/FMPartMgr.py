# -*- coding: utf-8 -*-

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
        return part.copy()

    def restore_part_info(self, snapshot, part):
        """[summary]

        Arguments:
            snapshot (type):  description

        Returns:
            dtype:  description
        """
        if isinstance(snapshot, list):
            for v, k in enumerate(snapshot):
                part[v] = k
        elif isinstance(snapshot, dict):
            for v, k in snapshot.items():
                part[v] = k
        else:
            raise NotImplementedError()
