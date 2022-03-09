from random import randint

from ckpttnpy.MLPartMgr import MLBiPartMgr, MLKWayPartMgr
from ckpttnpy.netlist import Netlist, create_drawf, read_json


def run_MLBiPartMgr(hgr: Netlist):
    partMgr = MLBiPartMgr(0.4)
    # partMgr.limitsize = 2000
    randseq = [randint(0, 1) for _ in hgr]

    if isinstance(hgr.modules, range):
        part = randseq
    elif isinstance(hgr.modules, list):
        part = {v: k for v, k in zip(hgr.modules, randseq)}
    else:
        raise NotImplementedError

    partMgr.run_FMPartition(hgr, hgr.module_weight, part)
    return partMgr.totalcost


def test_MLBiPartMgr():
    hgr = create_drawf()
    run_MLBiPartMgr(hgr)


def test_MLBiPartMgr2():
    hgr = read_json("testcases/p1.json")
    totalcost = run_MLBiPartMgr(hgr)
    assert totalcost >= 43
    assert totalcost <= 105


def run_MLKWayPartMgr(hgr: Netlist, num_parts: int):
    """[summary]

    Args:
        hgr (Netlist): [description]
        num_parts (int): [description]

    Returns:
        [type]: [description]
    """
    partMgr = MLKWayPartMgr(0.4, num_parts)
    # partMgr.limitsize = 2000
    randseq = [randint(0, num_parts - 1) for _ in hgr]

    if isinstance(hgr.modules, range):
        part = randseq
    elif isinstance(hgr.modules, list):
        part = {v: k for v, k in zip(hgr.modules, randseq)}
    else:
        raise NotImplementedError

    partMgr.run_FMPartition(hgr, hgr.module_weight, part)
    return partMgr.totalcost


def test_MLKWayPartMgr():
    hgr = read_json("testcases/p1.json")
    totalcost = run_MLKWayPartMgr(hgr, 3)
    assert totalcost >= 77
    assert totalcost <= 197


# if __name__ == "__main__":
#     test_MLKWayPartMgr()
