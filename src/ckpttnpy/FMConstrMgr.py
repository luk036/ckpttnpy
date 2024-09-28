"""
FMConstrMgr.py

This code defines a class called FMConstrMgr (Fiduccia-Mattheyses Constraint Manager) that helps manage constraints in a graph partitioning algorithm. The purpose of this code is to handle the balancing of weights when dividing a graph into different parts.

The main input for this class is a hypergraph (a type of graph where edges can connect more than two nodes), a balance tolerance value, module weights, and the number of parts to divide the graph into. The class doesn't produce a specific output, but it provides methods to check if moves between parts are legal and to update the balance of weights after moves.

The FMConstrMgr class achieves its purpose by keeping track of the weight differences between parts of the graph. It calculates a lower bound for the weight that each part should have to maintain balance. The class then provides methods to check if moving a node from one part to another would violate this balance constraint.

The main logic flow in this code involves initializing the weight differences, checking if moves are legal, and updating the weight differences after a move. The init method sets up the initial weight differences based on the current partition. The check_legal method determines if a proposed move is allowed based on the balance constraints. The update_move method adjusts the weight differences after a move has been made.

An important data transformation happening in this code is the calculation of the lower bound for part weights. This is done by taking the total weight of all nodes, multiplying it by a factor based on the number of parts, and then applying the balance tolerance.

The code also defines an enum called LegalCheck, which is used to represent different outcomes when checking if a move is legal. This helps in providing more detailed information about why a move might or might not be allowed.

Overall, this code provides a way to manage the constraints in a graph partitioning algorithm, ensuring that the parts remain balanced according to specified criteria. It's a crucial component in implementing the Fiduccia-Mattheyses algorithm for graph partitioning.
"""

from enum import Enum
from typing import TypeVar, Generic, Any, Dict, List, Union

# Define a generic type for the hypergraph nodes
Gnl = TypeVar("Gnl")

Part = Union[Dict[Any, int], List[int]]


class LegalCheck(Enum):
    """Check if the move of v can satisfied, GetBetter, or NotSatisfied

    The LegalCheck class is used to determine if a move can be satisfied, get better, or is not
    satisfied.

    Examples:
        >>> LegalCheck.NotSatisfied
        <LegalCheck.NotSatisfied: 0>
    """

    NotSatisfied = 0
    GetBetter = 1
    AllSatisfied = 2


class FMConstrMgr(Generic[Gnl]):
    """
    FMConstrMgr manages constraints for a given hypergraph in the Fiduccia-Mattheyses (FM) partitioning algorithm.
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
        self, hyprgraph: Gnl, bal_tol: float, module_weight, num_parts: int = 2
    ):
        """
        The function initializes the attributes of an object and calculates a lower bound value.

        :param hyprgraph: The `hyprgraph` parameter represents a list of values. It is not clear what these values
            represent without further context
        :param bal_tol: The `bal_tol` parameter represents the balance tolerance. It is a value that
            determines how balanced the weights of the parts should be. The lower the value, the more balanced
            the weights should be
        :param module_weight: The `module_weight` parameter represents the weight of each module
        :param num_parts: The `num_parts` parameter represents the number of parts or modules that the
            system is divided into. It is an optional parameter with a default value of 2, defaults to 2
            (optional)
        """
        self.hyprgraph = hyprgraph
        self.bal_tol = bal_tol
        self.module_weight = module_weight
        self.num_parts = num_parts
        self.diff = [0] * num_parts
        self.totalweight = sum(self.get_module_weight(v) for v in self.hyprgraph)
        totalweightK = self.totalweight * (2.0 / self.num_parts)
        self.lowerbound = round(totalweightK * self.bal_tol)

    def init(self, part: Part) -> None:
        """
        The `init` function initializes the `diff` list based on the module weights and the partition of the
        vertices.

        :param part: The `part` parameter is of type `Part` and it represents a partition of the nodes in a
            graph. Each node is assigned to a part, and the `part` parameter stores this assignment information
        :type part: Part
        """
        self.diff = [0] * self.num_parts
        for v in self.hyprgraph:
            self.diff[part[v]] += self.get_module_weight(v)

    def get_module_weight(self, node_index: int) -> int:
        """
        The function `get_module_weight` returns the weight of a module, given its index.

        :param node_index: The parameter `node_index` is of type `int` and it represents the index or key used to access
            the `module_weight` dictionary
        :return: the value of `1` if `self.module_weight` is `None`, otherwise it is returning the value of
            `self.module_weight[v]`.
        """
        return 1 if self.module_weight is None else self.module_weight[node_index]

    def check_legal(self, move_info_v) -> LegalCheck:
        """[summary]

        Arguments:
            from_part (type):  description
            v (type):  description

        Returns:
            dtype:  description
        """
        v, from_part, to_part = move_info_v
        self.weight = self.get_module_weight(v)
        diffFrom = self.diff[from_part] - self.weight
        if diffFrom < self.lowerbound:
            return LegalCheck.NotSatisfied  # not ok, don't move
        diffTo = self.diff[to_part] + self.weight
        if diffTo < self.lowerbound:
            return LegalCheck.GetBetter  # get better, but still illegal
        return LegalCheck.AllSatisfied  # all satisfied

    def check_constraints(self, move_info_v) -> bool:
        """
        The function `check_constraints` checks if a given move satisfies certain constraints.

        :param move_info_v: A tuple containing three elements: v, from_part, and an underscore
        :return: a boolean value.
        """
        v, from_part, _ = move_info_v
        self.weight = self.get_module_weight(v)
        diffFrom = self.diff[from_part] - self.weight
        return diffFrom >= self.lowerbound

    def update_move(self, move_info_v) -> None:
        """
        The `update_move` function updates the `diff` dictionary by adding the weight to the `to_part` key
        and subtracting the weight from the `from_part` key.

        :param move_info_v: The `move_info_v` parameter is a tuple containing three elements. The first
            element is not used in this method, so it is ignored. The second element, `from_part`, represents
            the part from which the move is being made. The third element, `to_part`, represents the part to
        """
        _, from_part, to_part = move_info_v
        self.diff[to_part] += self.weight
        self.diff[from_part] -= self.weight
