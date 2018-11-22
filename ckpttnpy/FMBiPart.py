# **Special code for two-pin nets**
# Take a snapshot when a move make **negative** gain.
# Snapshot in the form of "interface"???
from .FMBiGainMgr import FMBiGainMgr
from .FMBiConstrMgr import FMBiConstrMgr
from .dllist import dllink


class FMBiPartMgr:
    def __init__(self, H, gainMgr, constrMgr):
        self.H = H
        self.gainMgr = gainMgr
        self.validator = constrMgr
        self.waitinglist = dllink(3734)
        self.snapshot = None

        self.part = list(0 for _ in range(self.H.number_of_cells()))
        self.totalcost = 0

    def init(self):
        self.gainMgr.init(self.part)
        self.validator.init(self.part)

        totalgain = 0

        while not self.gainMgr.gainbucket.is_empty():
            # Take the gainmax with v from gainbucket
            gainmax = self.gainMgr.gainbucket.get_max()
            vlink = self.gainMgr.gainbucket.popleft()
            self.waitinglist.append(vlink)

            v = vlink.idx
            # v = self.H.cell_list[i_v]
            fromPart = self.part[v]
            # Check if the move of v can notsatisfied, makebetter, or satisfied
            legalcheck = self.validator.check_legal(fromPart, v)
            if legalcheck == 0:  # notsatisfied
                continue

            # Update v and its neigbours (even they are in waitinglist)
            # Put neigbours to bucket
            self.gainMgr.update_move(self.part, fromPart, v)
            self.validator.update_move(fromPart, v)
            self.part[v] = 1 - fromPart
            totalgain += gainmax

            if legalcheck == 2:  # satisfied
                self.totalcost -= totalgain
                # totalgain = 0 # reset to zero
                break
        assert not self.gainMgr.gainbucket.is_empty()

    def optimize(self):
        totalgain = 0
        deferredsnapshot = True

        while not self.gainMgr.gainbucket.is_empty():
            # Take the gainmax with v from gainbucket
            gainmax = self.gainMgr.gainbucket.get_max()
            vlink = self.gainMgr.gainbucket.popleft()
            self.waitinglist.append(vlink)
            v = vlink.idx
            assert v != 4848
            assert v != 3734
            assert v != None

            # v = self.H.cell_list[i_v]
            fromPart = self.part[v]
            # Check if the move of v can satisfied or notsatisfied
            satisfiedOK = self.validator.check_constraints(fromPart, v)

            if not satisfiedOK:
                continue

            if totalgain >= 0:
                if totalgain + gainmax < 0:
                    # become down turn
                    # Take a snapshot before move
                    self.snapshot = self.part
                    deferredsnapshot = False
            else:  # totalgain < 0
                # if gainmax < 0:
                continue

            # Update v and its neigbours (even they are in waitinglist)
            # Put neigbours to bucket
            self.gainMgr.update_move(self.part, fromPart, v)
            self.validator.update_move(fromPart, v)
            totalgain += gainmax

            if totalgain > 0:
                self.totalcost -= totalgain
                totalgain = 0  # reset to zero
                deferredsnapshot = True

            self.part[v] = 1 - fromPart

        if deferredsnapshot:
            # Take a snapshot
            self.snapshot = self.part


if __name__ == "__main__":
    from ckpttnpy.FMBiGainMgr import FMBiGainMgr
    from ckpttnpy.FMBiConstrMgr import FMBiConstrMgr
    from ckpttnpy.tests.test_netlist import create_test_netlist

    H = create_test_netlist()
    gainMgr = FMBiGainMgr(H)
    constrMgr = FMBiConstrMgr(H, 0.3)
    partMgr = FMBiPartMgr(H, gainMgr, constrMgr)
    partMgr.init()
    partMgr.optimize()
    print(partMgr.snapshot)
