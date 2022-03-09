# -*- coding: utf-8 -*-


# Take a snapshot when a move make **negative** gain.
# Snapshot in the form of "interface"???
from abc import abstractmethod

# **Special code for two-pin nets**
from typing import Any, Dict, List, Union

from .FMConstrMgr import LegalCheck

Part = Union[Dict[Any, int], List[int]]


class PartMgrBase:
    def __init__(self, hgr, gain_mgr, constrMgr):
        """[summary]

        Arguments:
            hgr (type):  description
            gain_mgr (type):  description
            constrMgr (type):  description
        """
        self.hgr = hgr
        self.gain_mgr = gain_mgr
        self.validator = constrMgr
        self.num_parts = gain_mgr.num_parts
        self.totalcost = 0

    def init(self, part: Part):
        """[summary]

        Arguments:
            part (type):  description
        """
        self.totalcost = self.gain_mgr.init(part)
        assert self.totalcost >= 0
        self.validator.init(part)

    def legalize(self, part: Part):
        """[summary]

        Arguments:
            part (type):  description

        Returns:
            dtype:  description
        """
        self.init(part)

        # Zero-weighted modules does not contribute legalization
        for v in filter(
            lambda v: self.hgr.get_module_weight(v) == 0
            and self.hgr.module_fixed is False,
            self.hgr,
        ):
            self.gain_mgr.lock_all(part[v], v)

        legalcheck = LegalCheck.NotSatisfied
        while legalcheck != LegalCheck.AllSatisfied:  # satisfied:
            # Take the gainmax with v from gainbucket
            # gainmax = self.gain_mgr.gainbucket.get_max()
            toPart = self.validator.select_togo()
            if self.gain_mgr.gainbucket[toPart]._max == 0:  # is_empty_togo()
                break
            v, gainmax = self.gain_mgr.select_togo(toPart)
            fromPart = part[v]
            assert fromPart != toPart
            move_info_v = v, fromPart, toPart
            # Check if the move of v can NotSatisfied, makebetter, or satisfied
            legalcheck = self.validator.check_legal(move_info_v)
            if legalcheck == LegalCheck.NotSatisfied:  # NotSatisfied
                continue

            # Update v and its neigbours (even they are in waitinglist)
            # Put neigbours to bucket
            self.gain_mgr.update_move(part, move_info_v)
            self.gain_mgr.update_move_v(move_info_v, gainmax)
            self.validator.update_move(move_info_v)
            part[v] = toPart
            self.totalcost -= gainmax
            assert self.totalcost >= 0
        return legalcheck

    def optimize(self, part: Part):
        """[summary]

        Arguments:
            part (type):  description
        """
        while True:
            self.init(part)
            totalcostbefore = self.totalcost
            self._optimize_1pass(part)
            assert self.totalcost <= totalcostbefore
            if self.totalcost == totalcostbefore:
                break

    def _optimize_1pass(self, part: Part):
        """[summary]

        Arguments:
            part (type):  description
        """
        totalgain = 0
        deferredsnapshot = False
        snapshot = None
        besttotalgain = 0

        while not self.gain_mgr.is_empty():
            # Take the gainmax with v from gainbucket
            move_info_v, gainmax = self.gain_mgr.select(part)
            # Check if the move of v can satisfied or NotSatisfied
            satisfiedOK = self.validator.check_constraints(move_info_v)
            if not satisfiedOK:
                continue
            if gainmax < 0:
                # become down turn
                if (not deferredsnapshot) or (totalgain > besttotalgain):
                    # Take a snapshot before move
                    snapshot = self.take_snapshot(part)
                    besttotalgain = totalgain
                deferredsnapshot = True

            elif totalgain + gainmax >= besttotalgain:
                besttotalgain = totalgain + gainmax
                deferredsnapshot = False

            # Update v and its neigbours (even they are in waitinglist)
            # Put neigbours to bucket
            v, _, toPart = move_info_v
            self.gain_mgr.lock(toPart, v)
            self.gain_mgr.update_move(part, move_info_v)
            self.gain_mgr.update_move_v(move_info_v, gainmax)
            self.validator.update_move(move_info_v)
            totalgain += gainmax
            part[v] = toPart

        if deferredsnapshot:
            # restore previous best solution
            self.restore_part_info(snapshot, part)
            totalgain = besttotalgain

        self.totalcost -= totalgain

    @abstractmethod
    def take_snapshot(self, part: Part):
        """[summary]

        Arguments:
            part (type):  description

        Returns:
            dtype:  description
        """

    @abstractmethod
    def restore_part_info(self, snapshot, part: Part):
        """[summary]

        Arguments:
            snapshot (type):  description

        Returns:
            dtype:  description
        """
