# -*- coding: utf-8 -*-
from enum import Enum
from typing import Any, Dict, List, Union

Part = Union[Dict[Any, int], List[int]]


class LegalCheck(Enum):
    """Check if the move of v can satisfied, GetBetter, or NotSatisfied

    Arguments:
        Enum {[type]} -- [description]
    """

    NotSatisfied = 0
    GetBetter = 1
    AllSatisfied = 2


class FMConstrMgr:
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

    def get_module_weight(self, v):
        """[summary]

        Arguments:
            v (size_t):  description

        Returns:
            [size_t]:  description
        """
        return 1 if self.module_weight is None else self.module_weight[v]

    def __init__(self, hgr, bal_tol, module_weight, num_parts=2):
        """[summary]

        Arguments:
            hgr (type):  description
            bal_tol (type):  description
        """
        self.hgr = hgr
        self.bal_tol = bal_tol
        self.module_weight = module_weight
        self.num_parts = num_parts
        self.diff = list(0 for _ in range(num_parts))
        self.totalweight = sum(self.get_module_weight(v) for v in self.hgr)
        totalweightK = self.totalweight * (2.0 / self.num_parts)
        self.lowerbound = round(totalweightK * self.bal_tol)

    def init(self, part: Part):
        """[summary]

        Arguments:
            part (type):  description
        """
        self.diff = list(0 for _ in range(self.num_parts))
        for v in self.hgr:
            self.diff[part[v]] += self.get_module_weight(v)

    def check_legal(self, move_info_v):
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

    def check_constraints(self, move_info_v):
        """[summary]

        Arguments:
            from_part (type):  description
            v (type):  description

        Returns:
            dtype:  description
        """
        v, from_part, _ = move_info_v
        self.weight = self.get_module_weight(v)
        diffFrom = self.diff[from_part] - self.weight
        return diffFrom >= self.lowerbound

    def update_move(self, move_info_v):
        """[summary]

        Arguments:
            from_part (type):  description
            v (type):  description
        """
        _, from_part, to_part = move_info_v
        self.diff[to_part] += self.weight
        self.diff[from_part] -= self.weight
