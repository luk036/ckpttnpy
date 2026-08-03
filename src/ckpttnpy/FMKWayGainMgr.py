"""K-way FM gain manager.

FMKWayGainMgr extends FMGainMgr with k-way partition support: maintains per-partition
gain buckets, round-robin key updates, and lock/unlock for fixed modules.
"""

from typing import Any, Dict, List, Union

from mywheel.robin import Robin  # for round-robin the partitions

from .FMGainMgr import FMGainMgr

Part = Union[Dict[Any, int], List[int]]


class FMKWayGainMgr(FMGainMgr):
    """
    The `FMKWayGainMgr` class is a subclass of `FMGainMgr` (Fiduccia-Mattheyses Gain Manager) that provides methods for initialization and
    reinitialization of a K-way partitioned netlist.
    """

    def __init__(self, GainCalc: Any, hyprgraph: Any, num_parts: int):

        FMGainMgr.__init__(self, GainCalc, hyprgraph, num_parts)
        self.rr = Robin(num_parts)

    def init(self, part: Part) -> int:

        totalcost = FMGainMgr.init(self, part)

        for bckt in self.gainbucket:
            bckt.clear()

        for v in self.hyprgraph:
            pv = part[v]
            for k in self.rr.exclude(pv):
                vlink = self.gain_calc.vertex_list[k][v]
                self.gainbucket[k].append(vlink, vlink.data[0])
            vlink = self.gain_calc.vertex_list[pv][v]
            self.gainbucket[pv].set_key(vlink, 0)
            self.waitinglist.append(vlink)

        for v in self.hyprgraph.module_fixed:
            self.lock_all(part[v], v)

        return totalcost

    def lock(self, whichPart: int, v: Any) -> None:

        vlink = self.gain_calc.vertex_list[whichPart][v]
        self.gainbucket[whichPart].detach(vlink)
        vlink.next = vlink  # lock

    def lock_all(self, _: Any, v: Any) -> None:

        for vlist, bckt in zip(self.gain_calc.vertex_list, self.gainbucket):
            vlink = vlist[v]
            bckt.detach(vlink)
            vlink.next = vlink  # lock

    def update_move_v(self, move_info_v: tuple[Any, int, int], gain: int) -> None:

        v, from_part, to_part = move_info_v
        for k in [k for k in self.rr.exclude(from_part) if k != to_part]:
            self.gainbucket[k].modify_key(
                self.gain_calc.vertex_list[k][v], self.gain_calc.delta_gain_v[k]
            )
        self._set_key(from_part, v, -gain)

    def modify_key(self, w: Any, part_w: int, key: Dict[int, int]) -> None:
        """
        The function `modify_key` modifies the key of a specific element in a dictionary.

        :param w: The parameter `w` is a variable of type that is not specified in the code snippet. It is
            used as an argument in the `modify_key` method
        :param part_w: The parameter `part_w` is not defined in the code snippet you provided. It seems to
            be missing or defined elsewhere in your code. Please provide more information or the definition of
            `part_w` so that I can assist you further
        :param key: The `key` parameter is a dictionary that contains keys and their corresponding values

        Examples:
            >>> from ckpttnpy.FMKWayGainCalc import FMKWayGainCalc
            >>> from netlistx.netlist import Netlist
            >>> import networkx as nx
            >>> modules = ['a1', 'a2', 'a3', 'a4']
            >>> nets = ['n1', 'n2', 'n3']
            >>> G = nx.Graph()
            >>> G.add_nodes_from(modules, bipartite=0)
            >>> G.add_nodes_from(nets, bipartite=1)
            >>> G.add_edges_from([('a1', 'n1'), ('a1', 'n2'), ('a1', 'n3')])
            >>> hyprgraph = Netlist(G, modules, nets)
            >>> mgr = FMKWayGainMgr(FMKWayGainCalc, hyprgraph, 3)
            >>> part = {v: 0 for v in hyprgraph}
            >>> part['a1'] = 1
            >>> _ = mgr.init(part)
            >>> mgr.modify_key('a1', 1, {0: 2, 2: 3})
            >>> mgr.gainbucket[0].get_max()
            2
            >>> mgr.gainbucket[2].get_max()
            3
        """
        for k in self.rr.exclude(part_w):
            self.gainbucket[k].modify_key(self.gain_calc.vertex_list[k][w], key[k])

    # private:

    def _set_key(self, whichPart: int, v: Any, key: int) -> None:

        self.gainbucket[whichPart].set_key(
            self.gain_calc.vertex_list[whichPart][v], key
        )
