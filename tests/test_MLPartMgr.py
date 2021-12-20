from random import randint

from ckpttnpy.MLPartMgr import MLBiPartMgr, MLKWayPartMgr
from ckpttnpy.netlist import Netlist, create_drawf, read_json


def run_MLBiPartMgr(H: Netlist):
    partMgr = MLBiPartMgr(0.4)
    # partMgr.limitsize = 2000
    randseq = [randint(0, 1) for _ in H]

    if isinstance(H.modules, range):
        part = randseq
    elif isinstance(H.modules, list):
        part = {v: k for v, k in zip(H.modules, randseq)}
    else:
        raise NotImplementedError

    partMgr.run_FMPartition(H, H.module_weight, part)
    return partMgr.totalcost


def test_MLBiPartMgr():
    H = create_drawf()
    run_MLBiPartMgr(H)


def test_MLBiPartMgr2():
    H = read_json("testcases/p1.json")
    totalcost = run_MLBiPartMgr(H)
    assert totalcost >= 43
    assert totalcost <= 105


def run_MLKWayPartMgr(H: Netlist, K: int):
    """[summary]

    Args:
        H (Netlist): [description]
        K (int): [description]

    Returns:
        [type]: [description]
    """
    partMgr = MLKWayPartMgr(0.4, K)
    # partMgr.limitsize = 2000
    randseq = [randint(0, K - 1) for _ in H]

    if isinstance(H.modules, range):
        part = randseq
    elif isinstance(H.modules, list):
        part = {v: k for v, k in zip(H.modules, randseq)}
    else:
        raise NotImplementedError

    partMgr.run_FMPartition(H, H.module_weight, part)
    return partMgr.totalcost


def test_MLKWayPartMgr():
    H = read_json("testcases/p1.json")
    totalcost = run_MLKWayPartMgr(H, 3)
    assert totalcost >= 77
    assert totalcost <= 197


# if __name__ == "__main__":
#     test_MLKWayPartMgr()
