# -*- coding: utf-8 -*-
from enum import Enum
from typing import Any, Dict, List, Union

Part = Union[Dict[Any, int], List[int]]


class LegalCheck(Enum):
    """Check if the move of v can satisfied, GetBetter, or NotSatisfied

    The LegalCheck class is used to determine if a move can be satisfied, get better, or is not
    satisfied.
    """

    NotSatisfied = 0
    GetBetter = 1
    AllSatisfied = 2


class FMConstrMgr:
    """_summary_

    The FMConstrMgr class represents a manager for constructing a finite element model, with various
    attributes related to weight, tolerance, module weight, number of parts, difference, total weight,
    and lower bound.
    """

    __slots__ = (
        "weight",
        "hgr",
        "bal_tol",
        "module_weight",
        "num_parts",
        "diff",
        "totalweight",
        "lowerbound",
    )

    def get_module_weight(self, v) -> int:
        """
        The function `get_module_weight` returns the weight of a module, given its index.

        :param v: The parameter `v` is of type `size_t` and it represents the index or key used to access
        the `module_weight` dictionary
        :return: the value of `1` if `self.module_weight` is `None`, otherwise it is returning the value of
        `self.module_weight[v]`.
        """
        return 1 if self.module_weight is None else self.module_weight[v]

    def __init__(self, hgr, bal_tol, module_weight, num_parts=2) -> None:
        """
        The function initializes the attributes of an object and calculates a lower bound value.

        :param hgr: The `hgr` parameter represents a list of values. It is not clear what these values
        represent without further context
        :param bal_tol: The `bal_tol` parameter represents the balance tolerance. It is a value that
        determines how balanced the weights of the parts should be. The lower the value, the more balanced
        the weights should be
        :param module_weight: The `module_weight` parameter represents the weight of each module
        :param num_parts: The `num_parts` parameter represents the number of parts or modules that the
        system is divided into. It is an optional parameter with a default value of 2, defaults to 2
        (optional)
        """
        self.hgr = hgr
        self.bal_tol = bal_tol
        self.module_weight = module_weight
        self.num_parts = num_parts
        self.diff = [0] * num_parts
        self.totalweight = sum(self.get_module_weight(v) for v in self.hgr)
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
        for v in self.hgr:
            self.diff[part[v]] += self.get_module_weight(v)

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
