# -*- coding: utf-8 -*-

from typing import Any, Dict, List, Union

from .lict import Lict
from .PartMgrBase import PartMgrBase

Part = Union[Dict[Any, int], List[int]]

# **Special code for two-pin nets**
# Take a snapshot when a move make **negative** gain.
# Snapshot in the form of "interface"???


class FMPartMgr(PartMgrBase):
    """The `FMPartMgr` class is a subclass of `PartMgrBase` that provides methods for taking snapshots of
    parts and restoring part information from a snapshot.
    """

    def take_snapshot(self, part: Part):
        """
        The `take_snapshot` function takes a `Part` object as input and returns a copy of it.

        :param part: The "part" parameter is of type "Part" and it represents the part that you want to take
        a snapshot of
        :type part: Part
        :return: a copy of the "part" object.
        """
        return part.copy()

    def restore_part_info(self, snapshot, part: Part):
        """
        The function `restore_part_info` takes a snapshot and updates the attributes of a `Part` object
        based on the snapshot.

        :param snapshot: The `snapshot` parameter is a variable that represents the data that needs to be
        restored. It can be either a list, a dictionary, or an object of type `Lict`
        :param part: The `part` parameter is an instance of the `Part` class
        :type part: Part
        """
        if isinstance(snapshot, list):
            for v, k in enumerate(snapshot):
                part[v] = k
        elif isinstance(snapshot, dict) or isinstance(snapshot, Lict):
            for v, k in snapshot.items():
                part[v] = k
        else:
            raise NotImplementedError()
