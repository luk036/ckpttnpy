"""
Benchmark comparing FM-only vs Multilevel (ML) partition manager on ibm01 and p1.

Runs both testcases with K={2,3,5}, BAL_TOL=0.45, LIMITSIZE=10.
"""

import time
from random import randint, seed

from netlistx.netlist import read_json
from netlistx.readwrite import read_are, read_netd

from ckpttnpy.FMBiConstrMgr import FMBiConstrMgr
from ckpttnpy.FMBiGainCalc import FMBiGainCalc
from ckpttnpy.FMBiGainMgr import FMBiGainMgr
from ckpttnpy.FMConstrMgr import LegalCheck
from ckpttnpy.FMKWayConstrMgr import FMKWayConstrMgr
from ckpttnpy.FMKWayGainCalc import FMKWayGainCalc
from ckpttnpy.FMKWayGainMgr import FMKWayGainMgr
from ckpttnpy.FMPartMgr import FMPartMgr
from ckpttnpy.MLPartMgr import MLBiPartMgr, MLKWayPartMgr

SEED = 42
NUM_RUNS = 5
BAL_TOL = 0.45
LIMITSIZE = 10
K_VALUES = [2, 3, 5]


def load_ibm01():
    """Load ibm01.net + ibm01.are into a Netlist."""
    hyprgraph = read_netd("testcases/ibm01.net")
    read_are(hyprgraph, "testcases/ibm01.are")
    return hyprgraph


def load_p1():
    """Load p1.json into a Netlist."""
    return read_json("testcases/p1.json")


def run_fm_only(hyprgraph, part, bal_tol, num_parts):
    """Run FM-only (single-level) partitioner, binary or k-way."""
    if num_parts == 2:
        gain_mgr = FMBiGainMgr(FMBiGainCalc, hyprgraph)
        constr_mgr = FMBiConstrMgr(hyprgraph, bal_tol, hyprgraph.module_weight, 2)
    else:
        gain_mgr = FMKWayGainMgr(FMKWayGainCalc, hyprgraph, num_parts)
        constr_mgr = FMKWayConstrMgr(
            hyprgraph, bal_tol, hyprgraph.module_weight, num_parts
        )
    part_mgr = FMPartMgr(hyprgraph, gain_mgr, constr_mgr)

    legal_check = part_mgr.legalize(part)
    if legal_check != LegalCheck.AllSatisfied:
        return None, None
    part_mgr.optimize(part)
    assert part_mgr.final_check(part)
    return part_mgr.totalcost, part_mgr.totalcost


def run_ml(hyprgraph, part, bal_tol, limitsize, num_parts):
    """Run multilevel partitioner, binary or k-way."""
    if num_parts == 2:
        part_mgr = MLBiPartMgr(bal_tol)
    else:
        part_mgr = MLKWayPartMgr(bal_tol, num_parts)
    part_mgr.limitsize = limitsize

    legal_check = part_mgr.run_Partition(hyprgraph, hyprgraph.module_weight, part)
    if legal_check != LegalCheck.AllSatisfied:
        return None, None
    return part_mgr.totalcost, part_mgr.totalcost


def run_benchmark(hyprgraph, name, num_parts):
    """Run NUM_RUNS of FM-only and ML for a given hypergraph and K."""
    print(f"\n  K={num_parts}")

    fm_costs = []
    ml_costs = []
    fm_times = []
    ml_times = []

    for run in range(NUM_RUNS):
        seed(SEED + run)
        r = [randint(0, num_parts - 1) for _ in hyprgraph]
        part_fm = {v: k for v, k in zip(hyprgraph.modules, r)}

        t0 = time.perf_counter()
        cost_fm, _ = run_fm_only(hyprgraph, part_fm, BAL_TOL, num_parts)
        t1 = time.perf_counter()
        elapsed_fm = t1 - t0

        if cost_fm is not None:
            fm_costs.append(cost_fm)
            fm_times.append(elapsed_fm)

        seed(SEED + run)
        r = [randint(0, num_parts - 1) for _ in hyprgraph]
        part_ml = {v: k for v, k in zip(hyprgraph.modules, r)}

        t0 = time.perf_counter()
        cost_ml, _ = run_ml(hyprgraph, part_ml, BAL_TOL, LIMITSIZE, num_parts)
        t1 = time.perf_counter()
        elapsed_ml = t1 - t0

        if cost_ml is not None:
            ml_costs.append(cost_ml)
            ml_times.append(elapsed_ml)

    if fm_costs:
        avg_fm = sum(fm_costs) / len(fm_costs)
        print(f"    FM-only:  cost={avg_fm:>8.1f}  time={sum(fm_times)/len(fm_times):.4f}s")
    else:
        print("    FM-only:  FAILED")
        avg_fm = None

    if ml_costs:
        avg_ml = sum(ml_costs) / len(ml_costs)
        print(f"    ML:       cost={avg_ml:>8.1f}  time={sum(ml_times)/len(ml_times):.4f}s")
    else:
        print("    ML:       FAILED")
        avg_ml = None

    if fm_costs and ml_costs:
        impr = (avg_fm - avg_ml) / avg_fm * 100
        rt = (sum(ml_times) / len(ml_times)) / (sum(fm_times) / len(fm_times))
        print(f"    ML improves cost by {impr:>+.1f}%,  {rt:.2f}x slower")
    print()


def main():
    print("=" * 70)
    print("Benchmark: FM-only vs Multilevel (ML) Partition Manager")
    print(f"BAL_TOL={BAL_TOL}, LIMITSIZE={LIMITSIZE}, K={K_VALUES}")
    print("=" * 70)

    for name, loader in [("ibm01", load_ibm01), ("p1", load_p1)]:
        print(f"\n{'=' * 70}")
        print(f"Testcase: {name}")
        print(f"{'=' * 70}")
        hyprgraph = loader()
        print(f"  Modules: {hyprgraph.number_of_modules()}, "
              f"Nets: {hyprgraph.number_of_nets()}")
        for num_parts in K_VALUES:
            run_benchmark(hyprgraph, name, num_parts)

    print("=" * 70)


if __name__ == "__main__":
    main()
