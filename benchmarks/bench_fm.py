"""Head-to-head runtime benchmark for ckpttn FM partitioning.

Replicates the C++ Google Benchmark structure:
- Reads ibm03.net + ibm03.are once (outside timed loop)
- Times legalize + optimize in a loop
- Reports average time per iteration

Usage:
    python benchmarks/bench_fm.py
"""

import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from netlistx.readwrite import read_netd, read_are
from netlistx.netlist import read_json
from ckpttnpy.FMBiGainCalc import FMBiGainCalc
from ckpttnpy.FMBiGainMgr import FMBiGainMgr
from ckpttnpy.FMBiConstrMgr import FMBiConstrMgr
from ckpttnpy.FMPartMgr import FMPartMgr


def run_fm_bi(hyprgraph, part):
    gain_mgr = FMBiGainMgr(FMBiGainCalc, hyprgraph)
    constr_mgr = FMBiConstrMgr(hyprgraph, 0.45, hyprgraph.module_weight)
    part_mgr = FMPartMgr(hyprgraph, gain_mgr, constr_mgr)
    part_mgr.legalize(part)
    part_mgr.optimize(part)


def benchmark_fm_bi(hyprgraph, name, iterations=5):
    part = [0] * hyprgraph.num_modules
    run_fm_bi(hyprgraph, list(part))

    times = []
    for _ in range(iterations):
        p = list(part)
        t0 = time.perf_counter()
        run_fm_bi(hyprgraph, p)
        t1 = time.perf_counter()
        times.append(t1 - t0)

    avg = sum(times) / len(times)
    print(f"  {name}: avg={avg*1000:.1f} ms over {iterations} runs "
          f"(min={min(times)*1000:.1f} ms, max={max(times)*1000:.1f} ms)")
    return avg


def main():
    testcases_dir = os.path.join(os.path.dirname(__file__), "..", "testcases")

    print("=== p1 (FMBi) ===")
    hyprgraph = read_json(os.path.join(testcases_dir, "p1.json"))
    print(f"  Modules: {hyprgraph.num_modules}, Nets: {hyprgraph.num_nets}")
    benchmark_fm_bi(hyprgraph, "p1 FMBi")

    print("\n=== ibm03 (FMBi) ===")
    hyprgraph = read_netd(os.path.join(testcases_dir, "ibm03.net"))
    read_are(hyprgraph, os.path.join(testcases_dir, "ibm03.are"))
    print(f"  Modules: {hyprgraph.num_modules}, Nets: {hyprgraph.num_nets}")
    benchmark_fm_bi(hyprgraph, "ibm03 FMBi", iterations=3)


if __name__ == "__main__":
    main()
