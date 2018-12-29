# **Special code for two-pin nets**
# Take a snapshot when a move make **negative** gain.
# Snapshot in the form of "interface"???


class FMPartMgr:
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
        # self.snapshot = None
        self.totalcost = 0

    def init(self, part):
        """[summary]
        """
        self.totalcost = self.gainMgr.init(part)
        # self.totalcost = self.gainMgr.totalcost
        assert self.totalcost >= 0
        self.validator.init(part)

        # totalgain = 0

    def legalize(self, part):
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
            # weight = self.H.get_module_weight(v)
            # Check if the move of v can notsatisfied, makebetter, or satisfied
            legalcheck = self.validator.check_legal(move_info_v)
            if legalcheck == 0:  # notsatisfied
                continue

            # Update v and its neigbours (even they are in waitinglist)
            # Put neigbours to bucket
            self.gainMgr.update_move(part, move_info_v)
            # weight = self.H.get_module_weight(v)
            # g = gainmax if weight != 0 else 2*self.gainMgr.pmax
            self.gainMgr.update_move_v(part, move_info_v, gainmax)
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

    def optimize_1pass(self, part):
        totalgain = 0
        deferredsnapshot = False
        # snapshot = part.copy()
        # snapshot = list(k for k in part)
        snapshot = None
        besttotalgain = 0

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
                    snapshot = list(k for k in part)
                    besttotalgain = totalgain
                deferredsnapshot = True

            elif totalgain + gainmax >= besttotalgain:
                besttotalgain = totalgain + gainmax
                deferredsnapshot = False

            # Update v and its neigbours (even they are in waitinglist)
            # Put neigbours to bucket
            _, toPart, v = move_info_v
            self.gainMgr.update_move(part, move_info_v)
            self.gainMgr.update_move_v(part, move_info_v, gainmax)
            self.gainMgr.lock(toPart, v)
            self.validator.update_move(move_info_v)
            totalgain += gainmax
            part[v] = toPart

        if deferredsnapshot:
            # restore previous best solution
            # part = snapshot.copy()
            # part = list(k for k in snapshot)
            for v, k in enumerate(snapshot):
                part[v] = k
            totalgain = besttotalgain

        self.totalcost -= totalgain

    def optimize(self, part):
        self.init(part)
        totalcostafter = self.totalcost
        while True:
            self.init(part)
            totalcostbefore = self.totalcost
            assert totalcostafter == totalcostbefore
            self.optimize_1pass(part)
            assert self.totalcost <= totalcostbefore
            if self.totalcost == totalcostbefore:
                break
            totalcostafter = self.totalcost
