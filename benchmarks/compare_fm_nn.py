"""Cross-language FM-vs-NN benchmark (Python side).

Configurations: {FM, NN} x {flat, multilevel} x {bi (k=2), k-way (k=3)}.
Initial partitions come from a SplitMix64 PRNG so that a given seed means the
same starting point in the C++ and Rust harnesses.

Usage:
    python benchmarks/compare_fm_nn.py [testcase ...]
"""

import json
import sys
import time

from netlistx.netlist import read_json
from netlistx.readwrite import read_are, read_netd

from ckpttnpy.partitioner import create_flat_part_mgr, create_partitioner

BAL_TOL = 0.45
LIMIT_SIZE = 50
SEEDS = [0, 1, 2, 3, 4]

MASK64 = (1 << 64) - 1


class SplitMix64:
    __slots__ = ("state",)

    def __init__(self, seed: int) -> None:
        self.state = seed & MASK64

    def next_u64(self) -> int:
        self.state = (self.state + 0x9E3779B97F4A7C15) & MASK64
        z = self.state
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & MASK64
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & MASK64
        return z ^ (z >> 31)

    def below(self, n: int) -> int:
        return self.next_u64() % n


def make_init(n: int, k: int, seed: int) -> list:
    rng = SplitMix64(seed)
    return [rng.below(k) for _ in range(n)]


def run_flat(hyprgraph, part: list, k: int, algo: str) -> int:
    mgr = create_flat_part_mgr(k, algo, BAL_TOL, hyprgraph, hyprgraph.module_weight)
    mgr.legalize(part)
    mgr.optimize(part)
    return mgr.totalcost


def run_ml(hyprgraph, part: list, k: int, algo: str) -> int:
    mgr = create_partitioner(k, algo, BAL_TOL, LIMIT_SIZE)
    mgr.run_Partition(hyprgraph, hyprgraph.module_weight, part)
    return mgr.totalcost


def load_testcases() -> dict:
    cases = {"p1": read_json("testcases/p1.json")}
    hg = read_netd("testcases/ibm03.net")
    read_are(hg, "testcases/ibm03.are")
    cases["ibm03"] = hg
    return cases


def main() -> None:
    all_cases = load_testcases()
    selected = sys.argv[1:] or list(all_cases)
    out = []
    for tc_name in selected:
        hyprgraph = all_cases[tc_name]
        n = hyprgraph.number_of_modules()
        for k in (2, 3):
            for algo in ("FM", "NN"):
                for ml in (False, True):
                    for seed in SEEDS:
                        part = make_init(n, k, seed)
                        t0 = time.perf_counter()
                        if ml:
                            cost = run_ml(hyprgraph, part, k, algo)
                        else:
                            cost = run_flat(hyprgraph, part, k, algo)
                        dt = time.perf_counter() - t0
                        rec = {
                            "lang": "py",
                            "testcase": tc_name,
                            "k": k,
                            "algo": algo,
                            "ml": ml,
                            "seed": seed,
                            "cost": int(cost),
                            "time_s": round(dt, 4),
                        }
                        out.append(rec)
                        print(json.dumps(rec), flush=True)
    with open("benchmarks/fmnn_results_py.json", "w") as f:
        json.dump(out, f, indent=1)


if __name__ == "__main__":
    main()
