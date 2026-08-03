"""Bi-partition gain manager for FM algorithm.

FMBiGainMgr extends FMGainMgr with 2-way specific initialization (toggle part),
locking, and key modification. Uses XOR (^ 1) to flip between partitions 0 and 1.
"""

from typing import Any, Dict, List, Union

from .FMGainMgr import FMGainMgr

Part = Union[Dict[Any, int], List[int]]


class FMBiGainMgr(FMGainMgr):
    """
    The `FMBiGainMgr` class is a subclass of `FMGainMgr` (Fiduccia-Mattheyses Gain
    Manager) that provides methods for initialization and reinitialization of a
    bi-partitioned netlist.
    """

    def init(self, part: Part) -> int:

        totalcost = FMGainMgr.init(self, part)

        for bckt in self.gainbucket:
            bckt.clear()
        for v in self.hyprgraph:
            vlink = self.gain_calc.vertex_list[v]
            to_part = part[v] ^ 1  # toggle 0 or 1
            self.gainbucket[to_part].appendleft_direct(vlink)
        for v in self.hyprgraph.module_fixed:
            self.lock_all(part[v], v)
        return totalcost

    def lock(self, whichPart: int, v: Any) -> None:

        vlink = self.gain_calc.vertex_list[v]
        self.gainbucket[whichPart].detach(vlink)
        vlink.next = vlink  # lock

    def lock_all(self, from_part: int, v: Any) -> None:

        self.lock(from_part ^ 1, v)

    def modify_key(self, w: Any, part_w: int, key: int) -> None:
        """
        The `modify_key` function updates the gain for a moving cell.

        :param w: The variable `w` represents the moving cell
        :param part_w: The `part_w` parameter represents a part or partition of a graph. It is used to
            determine which gainbucket to modify
        :param key: The `key` parameter is the new value for the gain of the moving cell

        Examples:
            >>> from ckpttnpy.FMBiGainCalc import FMBiGainCalc
            >>> from netlistx.netlist import Netlist
            >>> import networkx as nx
            >>> modules = ['a1', 'a2', 'a3', 'a4']
            >>> nets = ['n1', 'n2', 'n3']
            >>> G = nx.Graph()
            >>> G.add_nodes_from(modules, bipartite=0)
            >>> G.add_nodes_from(nets, bipartite=1)
            >>> G.add_edges_from([('a1', 'n1'), ('a1', 'n2'), ('a1', 'n3')])
            >>> hyprgraph = Netlist(G, modules, nets)
            >>> mgr = FMBiGainMgr(FMBiGainCalc, hyprgraph)
            >>> part = {v: 0 for v in hyprgraph}
            >>> part['a1'] = 1
            >>> _ = mgr.init(part)
            >>> mgr.modify_key('a1', 1, 3)
            >>> mgr.gainbucket[0].get_max()
            3
        """
        self.gainbucket[part_w ^ 1].modify_key(self.gain_calc.vertex_list[w], key)

    def update_move_v(self, move_info_v: tuple[Any, int, int], gain: int) -> None:

        v, from_part, _ = move_info_v
        self._set_key(from_part, v, -gain)

    # private:

    def _set_key(self, whichPart: int, v: Any, key: int) -> None:

        self.gainbucket[whichPart].set_key(self.gain_calc.vertex_list[v], key)
