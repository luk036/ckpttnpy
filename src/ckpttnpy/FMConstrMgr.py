"""Constraint manager for FM partitioning.

FMConstrMgr tracks partition weight differences and enforces balance constraints
during FM optimization. Provides LegalCheck enum (NotSatisfied, GetBetter, AllSatisfied)
for move legality determination based on lower bound calculations.
"""

from enum import Enum
from typing import Any, Dict, Generic, Iterable, List, TypeVar, Union

# Define a generic type for the hypergraph nodes
Gnl = TypeVar("Gnl", bound=Iterable[int])

Part = Union[Dict[Any, int], List[int]]


class LegalCheck(Enum):
    """Check if the move of v can satisfied, GetBetter, or NotSatisfied

    The LegalCheck class is used to determine if a move can be satisfied, get
    better, or is not satisfied.

    Examples:
        >>> LegalCheck.NotSatisfied
        <LegalCheck.NotSatisfied: 0>
    """

    NotSatisfied = 0
    GetBetter = 1
    AllSatisfied = 2


class FMConstrMgr(Generic[Gnl]):
    """
    FMConstrMgr manages constraints for a given hypergraph in the
    Fiduccia-Mattheyses (FM) partitioning algorithm.
    """

    __slots__ = (
        "weight",
        "hyprgraph",
        "bal_tol",
        "module_weight",
        "num_parts",
        "diff",
        "totalweight",
        "lowerbound",
    )

    def __init__(
        self, hyprgraph: Gnl, bal_tol: float, module_weight: Any, num_parts: int = 2
    ):
        self.hyprgraph = hyprgraph
        self.bal_tol = bal_tol
        self.module_weight = module_weight
        self.num_parts = num_parts
        self.diff = [0] * num_parts
        self.totalweight = sum(self.get_module_weight(v) for v in self.hyprgraph)
        totalweightK = self.totalweight * (2.0 / self.num_parts)
        self.lowerbound = round(totalweightK * self.bal_tol)

    def init(self, part: Part) -> None:
        self.diff = [0] * self.num_parts
        for v in self.hyprgraph:
            self.diff[part[v]] += self.get_module_weight(v)

    def get_module_weight(self, node_index: int) -> int:
        return 1 if self.module_weight is None else self.module_weight[node_index]

    def _get_diff_from(self, move_info_v: tuple) -> int:
        """Calculate the difference in weight of the partition from which a module is moved.

        :param move_info_v: A tuple containing the module to be moved, the partition it is moved from, and the partition it is moved to.
        :return: The difference in weight of the partition from which a module is moved.
        """
        v, from_part, _ = move_info_v
        self.weight = self.get_module_weight(v)
        diff_val = self.diff[from_part] - self.weight
        assert isinstance(diff_val, int)
        return diff_val

    def check_legal(self, move_info_v: tuple[Any, int, int]) -> LegalCheck:
        """Check if a move is legal under balance constraints.

        Args:
            move_info_v: Tuple of (vertex, from_part, to_part)

        Returns:
            LegalCheck: NotSatisfied, GetBetter, or AllSatisfied

        Examples:
            >>> hyprgraph = [0, 1, 2, 3, 4, 5, 6, 7, 8]
            >>> module_weight = [1, 1, 1, 1, 1, 1, 1, 1, 1]
            >>> mgr = FMConstrMgr(hyprgraph, 0.1, module_weight, 3)
            >>> part = [0, 0, 0, 1, 1, 1, 2, 2, 2]
            >>> mgr.init(part)
            >>> move_info_v = (0, 0, 1)
            >>> mgr.check_legal(move_info_v)
            <LegalCheck.AllSatisfied: 2>

        .. svgbob::

            "Constraint Checking for Module Move"

          +-------------------+-------------------+
          | Before Move       | After Move        |
          |                   |                   |
          | From Part: w=35   | From Part: w=25   |
          | [v1, v2, v3, v]   | [v1, v2, v3]      |
          | Lowerbound: w=30  | Lowerbound: w=30  |
          |                   |                   |
          | To Part: w=20     | To Part: w=30     |
          | [v4, v5]          | [v4, v5, v]       |
          | Lowerbound: w=30  | Lowerbound: w=30  |
          +-------------------+-------------------+

          Move is legal if both partitions meet lowerbound after move
        """

        diffFrom = self._get_diff_from(move_info_v)

        if diffFrom < self.lowerbound:
            return LegalCheck.NotSatisfied  # not ok, don't move

        _, _, to_part = move_info_v

        diffTo = self.diff[to_part] + self.weight

        if diffTo < self.lowerbound:
            return LegalCheck.GetBetter  # get better, but still illegal

        return LegalCheck.AllSatisfied  # all satisfied

    def check_constraints(self, move_info_v: tuple[Any, int, int]) -> bool:
        diffFrom = self._get_diff_from(move_info_v)
        return diffFrom >= self.lowerbound

    def update_move(self, move_info_v: tuple[Any, int, int]) -> None:
        _, from_part, to_part = move_info_v
        self.diff[to_part] += self.weight
        self.diff[from_part] -= self.weight

    def final_check(self, part: Part) -> bool:
        self.init(part)
        return all(diff >= self.lowerbound for diff in self.diff)
