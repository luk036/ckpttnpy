"""Fiduccia-Mattheyses Partition Manager.

FMPartMgr extends PartMgrBase with concrete snapshot/restore implementations
for the FM algorithm's backtracking mechanism. Supports both list and dict
partition representations.
"""

from mywheel.map_adapter import MapAdapter

from .PartMgrBase import Part, PartMgrBase


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

        .. svgbob::

            "Restoring Partition Information from Snapshot"
          +-------------------+       +-------------------+
          |  Snapshot State   |  -->  |   Current State   |
          |                   |       |                   |
          | [0, 1, 1, 0, 2]   |       | [1, 0, 1, 1, 2]   |
          |  v0 v1 v2 v3 v4   |       |  v0 v1 v2 v3 v4   |
          |  A  B  B  A  C    |       |  B  A  B  B  C    |
          +-------------------+       +-------------------+

          Restore partition assignments from a previous snapshot
        """

        if isinstance(snapshot, list):
            for v, k in enumerate(snapshot):
                part[v] = k
        elif isinstance(snapshot, dict) or isinstance(snapshot, MapAdapter):
            for v, k in snapshot.items():
                part[v] = k
        else:
            raise NotImplementedError()
