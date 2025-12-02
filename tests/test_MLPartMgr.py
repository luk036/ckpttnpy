from random import randint, seed

from netlistx.netlist import Netlist, read_json

from ckpttnpy.MLPartMgr import MLBiPartMgr, MLKWayPartMgr


def _run_MLBiPartMgr(hyprgraph: Netlist):
    part_mgr = MLBiPartMgr(0.4)
    # try: part_mgr.limitsize = 2000
    part_mgr.limitsize = 7
    randseq = [randint(0, 1) for _ in hyprgraph]

    if isinstance(hyprgraph.modules, range):
        part = randseq
    elif isinstance(hyprgraph.modules, list):
        part = {v: k for v, k in zip(hyprgraph.modules, randseq)}
    else:
        raise NotImplementedError

    part_mgr.run_FMPartition(hyprgraph, hyprgraph.module_weight, part)
    return part_mgr.totalcost


# def test_MLBiPartMgr():
#     hyprgraph = create_drawf()
#     _run_MLBiPartMgr(hyprgraph)


def test_MLBiPartMgr2():
    hyprgraph = read_json("testcases/p1.json")
    totalcost = _run_MLBiPartMgr(hyprgraph)
    assert totalcost >= 43
    assert totalcost <= 105


def _run_MLKWayPartMgr(hyprgraph: Netlist, num_parts: int):
    """
    The function `_run_MLKWayPartMgr` takes a hypergraph and the number of partitions as input, and
    returns the total cost of the partitioning.

    :param hyprgraph: The `hyprgraph` parameter is a Netlist object, which represents a hypergraph. It
    likely contains information about the modules and their connections in the hypergraph
    :type hyprgraph: Netlist
    :param num_parts: The `num_parts` parameter represents the number of partitions or parts that the
    hypergraph should be divided into
    :type num_parts: int
    :return: The function `_run_MLKWayPartMgr` returns the total cost of the partitioning performed by
    the `MLKWayPartMgr` object.
    """
    part_mgr = MLKWayPartMgr(0.4, num_parts)
    # try: part_mgr.limitsize = 2000
    randseq = [randint(0, num_parts - 1) for _ in hyprgraph]

    if isinstance(hyprgraph.modules, range):
        part = randseq
    elif isinstance(hyprgraph.modules, list):
        part = {v: k for v, k in zip(hyprgraph.modules, randseq)}
    else:
        raise NotImplementedError

    part_mgr.run_FMPartition(hyprgraph, hyprgraph.module_weight, part)
    return part_mgr.totalcost


def test_MLKWayPartMgr():
    seed(1234)
    hyprgraph = read_json("testcases/p1.json")
    totalcost = _run_MLKWayPartMgr(hyprgraph, 3)
    assert totalcost >= 77
    assert totalcost <= 197


# if __name__ == "__main__":
#     test_MLKWayPartMgr()
