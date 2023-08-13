from typing import Any, Dict, List, Union

from .FMGainMgr import FMGainMgr

Part = Union[Dict[Any, int], List[int]]


class FMBiGainMgr(FMGainMgr):
    """_summary_

    The `FMBiGainMgr` class is a subclass of `FMGainMgr` that provides methods for initialization and
    reinitialization of a partitioned netlist.
    """

    # public:

    # def __init__(self, GainCalc, hgr, num_parts=2):
    #     FMGainMgr.__init__(self, GainCalc, hgr)

    def init(self, part: Part) -> None:
        """
        The `init` function initializes the state of an object and performs some calculations based on the
        input `part`.

        :param part: The "part" parameter is a list that represents the partitioning of the vertices in the
        graph. Each element in the list corresponds to a vertex in the graph and indicates which partition
        the vertex belongs to (0 or 1)
        :type part: Part
        :return: the value of the variable "totalcost".
        """
        totalcost = FMGainMgr.init(self, part)

        for bckt in self.gainbucket:
            bckt.clear()
        for v in self.hgr:
            vlink = self.gain_calc.vertex_list[v]
            to_part = part[v] ^ 1  # toggle 0 or 1
            self.gainbucket[to_part].append_direct(vlink)
        for v in self.hgr.module_fixed:
            self.lock_all(part[v], v)
        return totalcost

    def lock(self, whichPart, v) -> None:
        """
        The `lock` function locks a vertex by detaching it from a gain bucket and setting its next pointer
        to itself.

        :param whichPart: whichPart is a variable of type uint8_t. It is used to specify which part of the
        code to lock
        :param v: The parameter `v` is of type `node_t` and represents a node in the graph
        """
        vlink = self.gain_calc.vertex_list[v]
        self.gainbucket[whichPart].detach(vlink)
        vlink.next = vlink  # lock

    def lock_all(self, from_part, v) -> None:
        """
        The function "lock_all" locks a specific part and its corresponding opposite part.

        :param from_part: The `from_part` parameter is of type `uint8_t` and is used to determine which part
        to lock
        :param v: The parameter "v" is of type "node_t"
        """
        """Lock

        Arguments:
            whichPart (uint8_t):  description
            v (node_t):  description
        """
        self.lock(from_part ^ 1, v)

    def modify_key(self, w, part_w, key):
        """
        The `modify_key` function updates the gain for a moving cell.

        :param w: The variable `w` represents the moving cell
        :param part_w: The `part_w` parameter represents a part or partition of a graph. It is used to
        determine which gainbucket to modify
        :param key: The `key` parameter is the new value for the gain of the moving cell
        """
        self.gainbucket[part_w ^ 1].modify_key(self.gain_calc.vertex_list[w], key)

    def update_move_v(self, move_info_v, gain) -> None:
        """
        The function `update_move_v` updates the value of a variable `v` by subtracting the `gain` from it.

        :param move_info_v: A tuple containing three elements: v, from_part, and an underscore variable
        :param gain: The `gain` parameter represents the amount of gain or loss in value that is associated
        with the move
        """
        v, from_part, _ = move_info_v
        self._set_key(from_part, v, -gain)

    # private:

    def _set_key(self, whichPart, v, key) -> None:
        """
        The `_set_key` function sets a key for a specific part and vertex in a gainbucket.

        :param whichPart: whichPart is a variable of type uint8_t, which represents a part or section of the
        gainbucket
        :param v: The parameter "v" is of type "node_t"
        :param key: The key parameter is an integer value that represents a key value
        """
        self.gainbucket[whichPart].set_key(self.gain_calc.vertex_list[v], key)
