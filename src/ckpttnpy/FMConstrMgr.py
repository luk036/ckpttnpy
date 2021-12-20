# -*- coding: utf-8 -*-
from enum import Enum
from typing import Any, Dict, List, Union

Part = Union[Dict[Any, int], List[int]]


class LegalCheck(Enum):
    """Check if the move of v can satisfied, getbetter, or notsatisfied

    Arguments:
        Enum {[type]} -- [description]
    """

    notsatisfied = 0
    getbetter = 1
    allsatisfied = 2


class FMConstrMgr:
    __slots__ = (
        "weight",
        "H",
        "BalTol",
        "module_weight",
        "K",
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

    def __init__(self, H, BalTol, module_weight, K=2):
        """[summary]

        Arguments:
            H (type):  description
            BalTol (type):  description
        """
        self.H = H
        self.BalTol = BalTol
        self.module_weight = module_weight
        self.K = K
        self.diff = list(0 for _ in range(K))
        self.totalweight = sum(self.get_module_weight(v) for v in self.H)
        totalweightK = self.totalweight * (2.0 / self.K)
        self.lowerbound = round(totalweightK * self.BalTol)

    def init(self, part: Part):
        """[summary]

        Arguments:
            part (type):  description
        """
        self.diff = list(0 for _ in range(self.K))
        for v in self.H:
            self.diff[part[v]] += self.get_module_weight(v)

    def check_legal(self, move_info_v):
        """[summary]

        Arguments:
            fromPart (type):  description
            v (type):  description

        Returns:
            dtype:  description
        """
        v, fromPart, toPart = move_info_v
        self.weight = self.get_module_weight(v)
        diffFrom = self.diff[fromPart] - self.weight
        if diffFrom < self.lowerbound:
            return LegalCheck.notsatisfied  # not ok, don't move
        diffTo = self.diff[toPart] + self.weight
        if diffTo < self.lowerbound:
            return LegalCheck.getbetter  # get better, but still illegal
        return LegalCheck.allsatisfied  # all satisfied

    def check_constraints(self, move_info_v):
        """[summary]

        Arguments:
            fromPart (type):  description
            v (type):  description

        Returns:
            dtype:  description
        """
        v, fromPart, _ = move_info_v
        self.weight = self.get_module_weight(v)
        diffFrom = self.diff[fromPart] - self.weight
        return diffFrom >= self.lowerbound

    def update_move(self, move_info_v):
        """[summary]

        Arguments:
            fromPart (type):  description
            v (type):  description
        """
        _, fromPart, toPart = move_info_v
        self.diff[toPart] += self.weight
        self.diff[fromPart] -= self.weight
