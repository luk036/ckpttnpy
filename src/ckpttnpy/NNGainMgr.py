"""No-Nonsense Gain Manager for FM partitioning.

NNGainMgr implements gain management without a waiting list (unlike FMGainMgr).
Used with NNPartMgr for simpler direct-optimization partitioning passes.
"""

from abc import abstractmethod
from typing import Any, Dict, List, Union

from mywheel.bpqueue import BPQueue
from mywheel.dllist import Dllink

Part = Union[Dict[Any, int], List[int]]

Item = Dllink[List[int]]


class NNGainMgr:
    """The `NNGainMgr` class is a base class for managing gains in Fiduccia-Mattheyses partitioning algorithm."""

    def __init__(self, GainCalc: Any, hyprgraph: Any, num_parts: int = 2) -> None:

    # public:


        self.hyprgraph = hyprgraph
        self.num_parts = num_parts
        self.gain_calc = GainCalc(hyprgraph, num_parts)
        self.pmax = self.hyprgraph.get_max_degree()
        self.gainbucket = [BPQueue(-self.pmax, self.pmax) for _ in range(num_parts)]

    def init(self, part: Part) -> int:

        totalcost = self.gain_calc.init(part)
        assert isinstance(totalcost, int)
        return totalcost

    def is_empty(self) -> bool:
        return all(bckt._max == 0 for bckt in self.gainbucket)

    def select(self, part: Part) -> tuple[tuple[Any, int, int], int]:

        to_part = max(range(self.num_parts), key=lambda k: self.gainbucket[k].get_max())
        maxk = self.gainbucket[to_part].get_max()

        vlink = self.gainbucket[to_part].popleft()
        v = vlink.data[1]
        from_part = part[v]
        move_info_v = v, from_part, to_part
        return move_info_v, maxk

    def select_togo(self, to_part: int) -> tuple[Any, int]:

        gainmax = self.gainbucket[to_part].get_max()
        vlink = self.gainbucket[to_part].popleft()
        v = vlink.data[1]
        return v, gainmax

    def update_move(self, part: Part, move_info_v: tuple[Any, int, int]) -> None:

        self.gain_calc.update_move_init()
        v, from_part, to_part = move_info_v
        for net in self.hyprgraph.ugraph[v]:
            degree = self.hyprgraph.ugraph.degree[net]
            if degree < 2:  # unlikely, self-loop, etc.
                continue  # does not provide any gain change when move
            move_info = [net, v, from_part, to_part]
            if degree == 2:
                self._update_move_net(
                    part, move_info, self.gain_calc.update_move_2pin_net
                )
            else:
                self.gain_calc.init_idx_vec(v, net)
                if degree == 3:
                    self._update_move_net(
                        part, move_info, self.gain_calc.update_move_3pin_net
                    )
                else:
                    self._update_move_net(
                        part, move_info, self.gain_calc.update_move_general_net
                    )

    @abstractmethod
    def modify_key(self, w: Any, part_w: int, key: Any) -> None:
        """
        The `modify_key` function is an abstract method that takes in three arguments (`w`, `part_w`, and
        `key`) and does not return anything.

        :param w: A node_t object. It is a parameter of the modify_key method and is used in the
            implementation of the method
        :param part_w: The parameter `part_w` is of type `node_t`
        :param key: The `key` parameter is of type `int` or `int[]`. It represents a key that will be
            modified in some way
        """

    # private:

    def _update_move_net(
        self, part: Part, move_info: list, gain_calc_method: Any
    ) -> None:

        delta_gain = gain_calc_method(part, move_info)
        if isinstance(delta_gain, (list, tuple)):
            for dGw, w in zip(delta_gain, self.gain_calc.idx_vec):
                self.modify_key(w, part[w], dGw)
        else:
            self.modify_key(delta_gain, part[delta_gain], self.gain_calc.delta_gain_w)
