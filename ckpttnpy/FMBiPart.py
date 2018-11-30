# **Special code for two-pin nets**
# Take a snapshot when a move make **negative** gain.
# Snapshot in the form of "interface"???


class FMBiPartMgr:
    def __init__(self, H, gainMgr, constrMgr):
        """[summary]

        Arguments:
            H {Netlist} -- [description]
            gainMgr {FMBiGainMgr} -- [description]
            constrMgr {FMBiConstrMgr} -- [description]
        """
        self.H = H
        self.gainMgr = gainMgr
        self.validator = constrMgr
        self.snapshot = None
        self.part = list(0 for _ in range(self.H.number_of_modules()))

        self.totalcost = 0

    def init(self):
        self.gainMgr.init(self.part)
        self.validator.init(self.part)

        totalgain = 0
        while not self.gainMgr.is_empty():
            # Take the gainmax with v from gainbucket
            v, gainmax = self.gainMgr.select()
            fromPart = self.part[v]
            toPart = 1 - fromPart
            move_info_v = fromPart, toPart, v
            # Check if the move of v can notsatisfied, makebetter, or satisfied
            legalcheck = self.validator.check_legal(move_info_v)

            if legalcheck == 0:  # notsatisfied
                continue

            # Update v and its neigbours (even they are in waitinglist)
            # Put neigbours to bucket
            self.gainMgr.update_move(self.part, move_info_v, gainmax)
            self.validator.update_move(move_info_v)
            self.part[v] = toPart
            totalgain += gainmax

            if legalcheck == 2:  # satisfied
                self.totalcost -= totalgain
                # totalgain = 0 # reset to zero
                break

    def optimize(self):
        totalgain = 0
        deferredsnapshot = True

        while not self.gainMgr.is_empty():
            # Take the gainmax with v from gainbucket
            v, gainmax = self.gainMgr.select()
            fromPart = self.part[v]
            toPart = 1 - fromPart
            move_info_v = fromPart, toPart, v
            # Check if the move of v can satisfied or notsatisfied
            satisfiedOK = self.validator.check_constraints(move_info_v)

            if not satisfiedOK:
                continue

            if totalgain >= 0:
                if totalgain + gainmax < 0:
                    # become down turn
                    # Take a snapshot before move
                    self.snapshot = self.part
                    deferredsnapshot = False
            else:  # totalgain < 0
                if gainmax <= 0:  # ???
                    continue

            # Update v and its neigbours (even they are in waitinglist)
            # Put neigbours to bucket
            self.gainMgr.update_move(self.part, move_info_v, gainmax)
            self.validator.update_move(move_info_v)
            totalgain += gainmax

            if totalgain > 0:
                self.totalcost -= totalgain
                totalgain = 0  # reset to zero
                deferredsnapshot = True

            self.part[v] = toPart

        if deferredsnapshot:
            # Take a snapshot
            self.snapshot = self.part
