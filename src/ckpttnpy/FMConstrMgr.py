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
    __slots__ = ('weight', 'H', 'BalTol', 'K',
                 'diff', 'totalweight', 'lowerbound')

    def __init__(self, H, BalTol, K=2):
        """[summary]

        Arguments:
            H (type):  description
            BalTol (type):  description
        """
        self.H = H
        self.BalTol = BalTol
        self.K = K
        self.diff = list(0 for _ in range(K))
        self.totalweight = 0
        for v in self.H.modules:
            weight = self.H.get_module_weight(v)
            self.totalweight += weight
        totalweightK = self.totalweight * (2. / self.K)
        self.lowerbound = round(totalweightK * self.BalTol)

    def init(self, part: Part):
        """[summary]

        Arguments:
            part (type):  description
        """
        self.diff = list(0 for _ in range(self.K))
        for v in self.H.modules:
            weight = self.H.get_module_weight(v)
            self.diff[part[v]] += weight

    def check_legal(self, move_info_v):
        """[summary]

        Arguments:
            fromPart (type):  description
            v (type):  description

        Returns:
            dtype:  description
        """
        v, fromPart, toPart = move_info_v
        self.weight = self.H.get_module_weight(v)
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
        self.weight = self.H.get_module_weight(v)
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
