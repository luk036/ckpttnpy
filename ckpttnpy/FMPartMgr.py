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
        self.snapshot = None
        self.totalcost = 0

    def init(self, part):
        """[summary]
        """
        self.gainMgr.init(part)
        self.totalcost = self.gainMgr.totalcost
        assert self.totalcost >= 0
        self.validator.init(part)

        # totalgain = 0

    def legalize(self, part):
        legalcheck = 0
        while True:
            # Take the gainmax with v from gainbucket
            # gainmax = self.gainMgr.gainbucket.get_max()
            toPart = self.validator.select_togo()
            if self.gainMgr.is_empty_togo(toPart):
                break
            v, i_v, gainmax = self.gainMgr.select_togo(toPart)
            fromPart = part[i_v]
            assert v == i_v
            assert fromPart != toPart
            move_info_v = [fromPart, toPart, v, i_v]
            # weight = self.H.get_module_weight(v)
            # Check if the move of v can notsatisfied, makebetter, or satisfied
            legalcheck = self.validator.check_legal(move_info_v)
            if legalcheck == 0:  # notsatisfied
                continue

            # Update v and its neigbours (even they are in waitinglist)
            # Put neigbours to bucket
            self.gainMgr.update_move(part, move_info_v)
            self.gainMgr.update_move_v(part, move_info_v, gainmax)
            self.validator.update_move(move_info_v)
            part[i_v] = toPart
            # totalgain += gainmax
            self.totalcost -= gainmax
            assert self.totalcost >= 0

            if legalcheck == 2:  # satisfied
                # self.totalcost -= totalgain
                # totalgain = 0 # reset to zero
                break

        return legalcheck
        # assert not self.gainMgr.gainbucket.is_empty()

    def optimize(self, part):
        """[summary]
        """
        totalgain = 0
        deferredsnapshot = False

        while not self.gainMgr.is_empty():
            # Take the gainmax with v from gainbucket
            # gainmax = self.gainMgr.gainbucket.get_max()
            move_info_v, gainmax = self.gainMgr.select(part)
            # Check if the move of v can satisfied or notsatisfied
            satisfiedOK = self.validator.check_constraints(move_info_v)

            if not satisfiedOK:
                continue

            if totalgain >= 0:
                if totalgain + gainmax < 0:
                    # become down turn
                    # Take a snapshot before move
                    self.snapshot = part
                    deferredsnapshot = False
                else:
                    deferredsnapshot = True
            else:  # totalgain < 0
                if gainmax <= 0:  # ???
                    continue
                else:
                    deferredsnapshot = True

            # Update v and its neigbours (even they are in waitinglist)
            # Put neigbours to bucket
            self.gainMgr.update_move(part, move_info_v)
            self.gainMgr.update_move_v(part, move_info_v, gainmax)
            self.validator.update_move(move_info_v)
            totalgain += gainmax

            if totalgain > 0:
                self.totalcost -= totalgain
                assert self.totalcost >= 0
                totalgain = 0  # reset to zero
                # deferredsnapshot = True

            _, toPart, _, i_v = move_info_v
            part[i_v] = toPart

        if deferredsnapshot:
            # restore previous best solution
            part = self.snapshot

