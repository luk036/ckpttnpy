from random import randint

from ckpttnpy.MLPartMgr import MLBiPartMgr, MLKWayPartMgr
from ckpttnpy.netlist import Netlist, create_drawf, read_json


def run_MLBiPartMgr(H: Netlist):
    partMgr = MLBiPartMgr(0.4)
    mincost = 1000
    for _ in range(10):
        randseq = [randint(0, 1) for _ in range(H.number_of_modules())]

        if isinstance(H.modules, range):
            part = randseq
        elif isinstance(H.modules, list):
            part = {v: k for v, k in zip(H.modules, randseq)}
        else:
            raise NotImplementedError

        partMgr.run_FMPartition(H, H.module_weight, part)
        if mincost > partMgr.totalcost:
            mincost = partMgr.totalcost
    return mincost


def test_MLBiPartMgr():
    H = create_drawf()
    # totalcost =
    run_MLBiPartMgr(H)
    # assert totalcost == 2 # ???


def test_MLBiPartMgr2():
    H = read_json('testcases/p1.json')
    totalcost = run_MLBiPartMgr(H)
    # assert totalcost >= 55
    # assert totalcost <= 70
    assert totalcost >= 43
    assert totalcost <= 65


# def test_MLBiPartMgr3():
#     H = create_random_graph()
#     totalcost = run_MLBiPartMgr(H)
#     # assert totalcost >= 55
#     # assert totalcost <= 70
#     assert totalcost >= 5
#     assert totalcost <= 5


def run_MLKWayPartMgr(H: Netlist, K: int):
    partMgr = MLKWayPartMgr(0.4, K)
    mincost = 1000
    for _ in range(10):
        randseq = [randint(0, K-1) for _ in range(H.number_of_modules())]
        part = list(randseq)
        partMgr.run_FMPartition(H, H.module_weight, part)
        if mincost > partMgr.totalcost:
            mincost = partMgr.totalcost
    return mincost


# def test_MLKWayPartMgr():
#     H = create_drawf()
#     # totalcost =
#     run_MLKWayPartMgr(H, 3)
#     # assert totalcost == 4 # ???


def test_MLKWayPartMgr2():
    H = read_json('testcases/p1.json')
    totalcost = run_MLKWayPartMgr(H, 3)
    # assert totalcost >= 109
    # assert totalcost <= 152
    assert totalcost >= 77
    assert totalcost <= 147


# def test_MLKWayPartMgr3():
#     H = create_random_graph()
#     totalcost = run_MLKWayPartMgr(H, 3)
#     # assert totalcost >= 109
#     # assert totalcost <= 152
#     assert totalcost >= 9
#     assert totalcost <= 9


# if __name__ == "__main__":
#     test_MLKWayPartMgr()
