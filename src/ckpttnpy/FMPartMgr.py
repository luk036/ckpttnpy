"""
FMPartMgr.py

This code defines a class called FMPartMgr (Fiduccia-Mattheyses Partitioning Manager) that helps manage partitions in a graph or network. The main purpose of this code is to provide methods for taking snapshots of partitions and restoring partition information from those snapshots.

The FMPartMgr class is designed to work with "parts," which can be either dictionaries or lists containing integer values. These parts likely represent different sections or groups within a larger system or network.

The class has two main methods: take_snapshot and restore_part_info. The take_snapshot method simply creates a copy of the current partition state. This is useful for saving the current state of the partition before making changes, allowing you to revert to this state if needed later.

The restore_part_info method does the opposite - it takes a previously saved snapshot and uses it to update the current partition. This method can handle snapshots in different formats (list or dictionary), and it updates the partition by assigning values from the snapshot to the corresponding elements in the current partition.

The code achieves its purpose through simple copy and assignment operations. For taking a snapshot, it uses the copy method to create a duplicate of the current partition. For restoring, it iterates through the snapshot data and assigns each value to the corresponding position in the current partition.

An important aspect of the logic is the flexibility in handling different data types. The restore_part_info method checks whether the snapshot is a list, a dictionary, or a special type called MapAdapter (likely a custom data structure). Depending on the type, it uses different methods to iterate through the data and update the partition.

Overall, this code provides a simple way to save and restore the state of partitions in a graph or network, which can be useful in algorithms that involve iterative improvements or need to backtrack to previous states.
"""

from typing import Any, Dict, List, Union

from mywheel.map_adapter import MapAdapter

from .PartMgrBase import PartMgrBase

Part = Union[Dict[Any, int], List[int]]

# **Special code for two-pin nets**
# Take a snapshot when a move make **negative** gain.
# Snapshot in the form of "interface"???


class FMPartMgr(PartMgrBase):
    """Fiduccia-Mattheyses Partitioning Manager

    The `FMPartMgr` class is a subclass of `PartMgrBase` that provides methods for taking snapshots of
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
            restored. It can be either a list, a dictionary, or an object of type `MapAdapter`
        :param part: The `part` parameter is an instance of the `Part` class
        :type part: Part
        """
        if isinstance(snapshot, list):
            for v, k in enumerate(snapshot):
                part[v] = k
        elif isinstance(snapshot, dict) or isinstance(snapshot, MapAdapter):
            for v, k in snapshot.items():
                part[v] = k
        else:
            raise NotImplementedError()
