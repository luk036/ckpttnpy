# **Special code for two-pin nets**
# Take a snapshot when a move make **negative** gain.
# Snapshot in the form of "interface"???
from collections import deque


class FDPartMgr:
    def __init__(self, H, gainMgr, constrMgr):
        """[summary]

        Arguments:
            H {[type]} -- [description]
            gainMgr {[type]} -- [description]
            constrMgr {[type]} -- [description]
        """
        self.H = H
        self.gainMgr = gainMgr
        self.validator = constrMgr
        self.K = gainMgr.K
        self.totalcost = 0

    def init(self, part_info):
        """[summary]

        Arguments:
            part_info {[type]} -- [description]
        """
        self.totalcost = self.gainMgr.init(part_info)
        # self.totalcost = self.gainMgr.totalcost
        assert self.totalcost >= 0
        part, _ = part_info
        self.validator.init(part)

        # totalgain = 0

    def legalize(self, part_info):
        """[summary]

        Arguments:
            part_info {[type]} -- [description]

        Returns:
            [type] -- [description]
        """
        part, _ = part_info
        self.init(part_info)
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
            # weight = self.H.get_module_weight(v)
            # Check if the move of v can notsatisfied, makebetter, or satisfied
            legalcheck = self.validator.check_legal(move_info_v)
            if legalcheck == 0:  # notsatisfied
                continue

            # Update v and its neigbours (even they are in waitinglist)
            # Put neigbours to bucket
            self.gainMgr.update_move(part_info, move_info_v)
            weight = self.H.get_module_weight(v)
            g = gainmax if weight != 0 else 2*self.gainMgr.pmax
            self.gainMgr.update_move_v(part_info, move_info_v, g)
            self.validator.update_move(move_info_v)
            part[v] = toPart
            # totalgain += gainmax
            self.totalcost -= gainmax
            assert self.totalcost >= 0

            if legalcheck == 2:  # satisfied
                # self.totalcost -= totalgain
                # totalgain = 0 # reset to zero
                break

        return legalcheck
        # assert not self.gainMgr.gainbucket.is_empty()

    def optimize(self, part_info):
        """[summary]

        Arguments:
            part_info {[type]} -- [description]
        """
        self.init(part_info)
        totalcostafter = self.totalcost
        while True:
            self.init(part_info)
            totalcostbefore = self.totalcost
            assert totalcostafter == totalcostbefore
            self.optimize_1pass(part_info)
            assert self.totalcost <= totalcostbefore
            if self.totalcost == totalcostbefore:
                break
            totalcostafter = self.totalcost

    def optimize_1pass(self, part_info):
        """[summary]

        Arguments:
            part_info {[type]} -- [description]
        """
        totalgain = 0
        deferredsnapshot = False
        # snapshot = part.copy()
        # snapshot = list(k for k in part)
        snapshot = None
        besttotalgain = -1
        part, _ = part_info

        while not self.gainMgr.is_empty():
            # Take the gainmax with v from gainbucket
            # gainmax = self.gainMgr.gainbucket.get_max()
            move_info_v, gainmax = self.gainMgr.select(part)
            # Check if the move of v can satisfied or notsatisfied
            satisfiedOK = self.validator.check_constraints(move_info_v)
            if not satisfiedOK:
                continue
            if gainmax < 0:
                # become down turn
                if (not deferredsnapshot) or (totalgain > besttotalgain):
                    # Take a snapshot before move
                    # snapshot = part.copy()
                    snapshot = self.take_snapshot(part_info)
                    besttotalgain = totalgain
                deferredsnapshot = True

            elif totalgain + gainmax > besttotalgain:
                besttotalgain = totalgain + gainmax
                deferredsnapshot = False

            # Update v and its neigbours (even they are in waitinglist)
            # Put neigbours to bucket
            self.gainMgr.update_move(part_info, move_info_v)
            self.gainMgr.update_move_v(part, move_info_v, 2*self.gainMgr.pmax)
            self.validator.update_move(move_info_v)
            totalgain += gainmax
            _, toPart, v = move_info_v
            part[v] = toPart

        if deferredsnapshot:
            # restore previous best solution
            # part = snapshot.copy()
            part_info = self.restore_part_info(snapshot)
            totalgain = besttotalgain

        self.totalcost -= totalgain

    def take_snapshot(self, part_info):
        """[summary]

        Arguments:
            part_info {[type]} -- [description]

        Returns:
            [type] -- [description]
        """
        part, extern_nets = part_info
        extern_nets_ss = extern_nets.copy()
        extern_modules_ss = dict()
        for net in extern_nets:
            for v in self.H.G[net]:
                extern_modules_ss[v] = part[v]
        return extern_nets_ss, extern_modules_ss

    def restore_part_info(self, snapshot):
        """[summary]

        Arguments:
            snapshot {[type]} -- [description]

        Returns:
            [type] -- [description]
        """
        extern_nets_ss, extern_modules_ss = snapshot
        part = list(self.K for _ in range(self.H.number_of_modules()))
        Q = deque(v for v, _ in extern_modules_ss.items())
        while Q:
            v = Q.popleft()
            if part[v] < self.K:
                continue
            part_v = part[v] = extern_modules_ss[v]
            Q2 = deque()
            Q2.append(v)
            while Q2:
                v2 = Q2.popleft()
                # if part[v2] < self.K:
                #     continue
                for net in self.H.G[v2]:
                    if net in extern_nets_ss:
                        continue
                    for v3 in self.H.G[net]:
                        if part[v3] < self.K:
                            continue
                        part[v3] = part_v
                        Q2.append(v3)
        extern_nets = extern_nets_ss.copy()
        return part, extern_nets
