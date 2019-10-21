# -*- coding: utf-8 -*-


# Take a snapshot when a move make **negative** gain.
# Snapshot in the form of "interface"???
from abc import abstractmethod
# **Special code for two-pin nets**
from typing import Any, Dict, List, Union

Part = Union[Dict[Any, int], List[int]]


class PartMgrBase:
    def __init__(self, H, gainMgr, constrMgr):
        """[summary]

        Arguments:
            H (type):  description
            gainMgr (type):  description
            constrMgr (type):  description
        """
        self.H = H
        self.gainMgr = gainMgr
        self.validator = constrMgr
        self.K = gainMgr.K
        self.totalcost = 0

    def init(self, part: Part):
        """[summary]

        Arguments:
            part (type):  description
        """
        self.totalcost = self.gainMgr.init(part)
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
        for v in self.H.modules:
            if self.H.get_module_weight(v) != 0:
                continue
            if v in self.H.module_fixed:  # already locked
                continue
            self.gainMgr.lock_all(part[v], v)

        legalcheck = 0
        while True:
            # Take the gainmax with v from gainbucket
            # gainmax = self.gainMgr.gainbucket.get_max()
            toPart = self.validator.select_togo()
            if self.gainMgr.is_empty_togo(toPart):
                break
            v, gainmax = self.gainMgr.select_togo(toPart)
            fromPart = part[v]
            assert fromPart != toPart
            move_info_v = [fromPart, toPart, v]
            # Check if the move of v can notsatisfied, makebetter, or satisfied
            legalcheck = self.validator.check_legal(move_info_v)
            if legalcheck == 0:  # notsatisfied
                continue

            # Update v and its neigbours (even they are in waitinglist)
            # Put neigbours to bucket
            self.gainMgr.update_move(part, move_info_v)
            self.gainMgr.update_move_v(move_info_v, gainmax)
            self.validator.update_move(move_info_v)
            part[v] = toPart
            self.totalcost -= gainmax
            assert self.totalcost >= 0

            if legalcheck == 2:  # satisfied
                break

        return legalcheck

    def optimize(self, part: Part):
        """[summary]

        Arguments:
            part (type):  description
        """
        while True:
            self.init(part)
            totalcostbefore = self.totalcost
            self.__optimize_1pass(part)
            assert self.totalcost <= totalcostbefore
            if self.totalcost == totalcostbefore:
                break

    def __optimize_1pass(self, part: Part):
        """[summary]

        Arguments:
            part (type):  description
        """
        totalgain = 0
        deferredsnapshot = False
        snapshot = None
        besttotalgain = 0

        while not self.gainMgr.is_empty():
            # Take the gainmax with v from gainbucket
            move_info_v, gainmax = self.gainMgr.select(part)
            # Check if the move of v can satisfied or notsatisfied
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
            _, toPart, v = move_info_v
            self.gainMgr.lock(toPart, v)
            self.gainMgr.update_move(part, move_info_v)
            self.gainMgr.update_move_v(move_info_v, gainmax)
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
