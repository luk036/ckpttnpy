# **Special code for two-pin nets**
# Take a snapshot when a move make **negative** gain.
# Snapshot in the form of "interface"???
from .FMKWayGainMgr import FMKWayGainMgr
from .FMKWayConstrMgr import FMKWayConstrMgr


class FMKWayPartMgr:
    def __init__(self, H, K, gainMgr, constrMgr):
        """[summary]

        Arguments:
            H {[type]} -- [description]
            gainMgr {[type]} -- [description]
            constrMgr {[type]} -- [description]
        """
        self.H = H
        self.K = K
        self.gainMgr = gainMgr
        self.validator = constrMgr
        self.snapshot = None

        self.part = list(0 for _ in range(self.H.number_of_cells()))
        self.totalcost = 0

    def init(self):
        """[summary]
        """
        self.gainMgr.init(self.part)
        self.validator.init(self.part)

        totalgain = 0

        while True: 
            # Take the gainmax with v from gainbucket
            # gainmax = self.gainMgr.gainbucket.get_max()
            toPart = self.validator.select_togo()
            if self.gainMgr.is_empty(toPart):
                break
            v, gainmax = self.gainMgr.select_togo(toPart)
            # v = self.H.cell_list[i_v]
            fromPart = self.part[v]
            # weight = self.H.G.nodes[v].get('weight', 1)
            # Check if the move of v can notsatisfied, makebetter, or satisfied
            legalcheck = self.validator.check_legal(fromPart, toPart, v)
            if legalcheck == 0:  # notsatisfied
                continue

            # Update v and its neigbours (even they are in waitinglist)
            # Put neigbours to bucket
            self.gainMgr.update_move(self.part, fromPart, toPart, v, gainmax)
            self.validator.update_move(fromPart, toPart, v)
            self.part[v] = toPart
            totalgain += gainmax

            if legalcheck == 2:  # satisfied
                self.totalcost -= totalgain
                # totalgain = 0 # reset to zero
                break
        # assert not self.gainMgr.gainbucket.is_empty()

    def optimize(self):
        """[summary]
        """
        totalgain = 0
        deferredsnapshot = True

        while True: 
            # Take the gainmax with v from gainbucket
            # gainmax = self.gainMgr.gainbucket.get_max()
            toPart = self.validator.select_togo()
            if self.gainMgr.is_empty(toPart):
                break
            v, gainmax = self.gainMgr.select_togo(toPart)
            # v = self.H.cell_list[i_v]
            fromPart = self.part[v]
            # Check if the move of v can satisfied or notsatisfied
            # weight = self.H.G.nodes[v].get('weight', 1)
            satisfiedOK = self.validator.check_constraints(fromPart, toPart, v)

            if not satisfiedOK:
                continue

            if totalgain >= 0:
                if totalgain + gainmax < 0:
                    # become down turn
                    # Take a snapshot before move
                    self.snapshot = self.part
                    deferredsnapshot = False
            else:  # totalgain < 0
                if gainmax <= 0: # ???
                    continue

            # Update v and its neigbours (even they are in waitinglist)
            # Put neigbours to bucket
            self.gainMgr.update_move(self.part, fromPart, toPart, v, gainmax)
            self.validator.update_move(fromPart, toPart, v)
            totalgain += gainmax

            if totalgain > 0:
                self.totalcost -= totalgain
                totalgain = 0  # reset to zero
                deferredsnapshot = True

            self.part[v] = toPart

        if deferredsnapshot:
            # Take a snapshot
            self.snapshot = self.part


def run_FMKWayPartMgr(H, gainMgr):
    constrMgr = FMKWayConstrMgr(H, 3, 0.7)
    partMgr = FMKWayPartMgr(H, 3, gainMgr, constrMgr)
    partMgr.init()
    totalcostbefore = partMgr.totalcost
    partMgr.optimize()
    assert partMgr.totalcost <= totalcostbefore
    print(partMgr.snapshot)


if __name__ == "__main__":
    from ckpttnpy.tests.test_netlist import create_test_netlist, create_drawf

    H = create_drawf()
    gainMgr = FMKWayGainMgr(H, 3)
    run_FMKWayPartMgr(H, gainMgr)
