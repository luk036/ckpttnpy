# FM-only vs Multilevel (ML) Partition Manager — Benchmark Report

## 1. Overview

This report compares two partitioning algorithms implemented in `ckpttnpy`:

- **FM-only**: Single-level Fiduccia-Mattheyses partitioning (`FMPartMgr` + `FMBiGainMgr` + `FMBiConstrMgr`)
- **ML (Multilevel)**: Multi-level Fiduccia-Mattheyses partitioning (`MLBiPartMgr`) with graph contraction prior to FM optimization

Both partitioners perform **2-way (binary) hypergraph partitioning** with balance constraints.

> **Note on runtime**: All measurements are wall-clock times from a Python implementation and are provided for **relative comparison only**. Absolute runtime depends heavily on the Python interpreter, data structure overhead, and hardware. A C++ implementation would be orders of magnitude faster. Do not treat these numbers as production performance benchmarks.

### Testcase

| Property  | Value |
|-----------|-------|
| Benchmark | ibm01 (IBM-PLACE format) |
| Modules   | 12,752 (12,505 cells + 247 pads) |
| Nets      | 14,111 |
| Weights   | ibm01.are (module area weights) |

### Configuration

| Parameter        | Value |
|------------------|-------|
| Balance tolerance (bal_tol) | 0.4 |
| ML limitsize     | 2000 |
| Random seeds     | 42–46 (5 runs) |
| Python           | 3.x |

---

## 2. Methodology

For each of 5 runs, both partitioners receive identical random initial partitions (same seed per run). The full pipeline is:

1. Load `ibm01.net` via `read_netd()`, load `ibm01.are` via `read_are()`
2. Generate random initial partition: each module assigned to part 0 or 1 with equal probability
3. Run **FM-only**:
   - Build `FMBiGainMgr`, `FMBiConstrMgr`, `FMPartMgr`
   - Call `legalize()` to satisfy balance constraints
   - Call `optimize()` (iterative FM passes until convergence)
4. Run **ML**:
   - Build `MLBiPartMgr` with `limitsize=2000`
   - Call `run_Partition()` which contracts the graph recursively when `num_modules ≥ limitsize`, then optimizes at each level
5. Record cut cost and wall-clock time for each run

---

## 3. Results

### 3.1 Raw Data

| Run | FM-only Cut Cost | FM-only Runtime (s) | ML Cut Cost | ML Runtime (s) |
|-----|-----------------|---------------------|-------------|-----------------|
| 1   | 373             | 9.52                | 346         | 32.33           |
| 2   | 345             | 18.03               | 289         | 23.01           |
| 3   | 448             | 10.61               | 393         | 38.13           |
| 4   | 709             | 16.82               | 521         | 34.50           |
| 5   | 492             | 17.97               | 329         | 21.86           |

### 3.2 Cut Cost Comparison

| Metric        | FM-only | ML      | Reduction |
|---------------|---------|---------|-----------|
| **Average**   | 473.4   | **375.6** | **20.7%** |
| **Minimum**   | 345     | **289** | **16.2%** |
| **Maximum**   | 709     | **521** | **26.5%** |
| **Std Dev**   | 136.9   | 88.6    | —         |

ML achieves a **lower cut cost on every single run**. The average reduction is 20.7%.

### 3.3 Runtime Comparison

| Metric        | FM-only | ML      | Ratio  |
|---------------|---------|---------|--------|
| **Average**   | 14.59s  | 29.97s  | **2.05×** |
| **Minimum**   | 9.52s   | 21.86s  | 2.30×  |
| **Maximum**   | 18.03s  | 38.13s  | 2.12×  |

ML is approximately **2× slower** than FM-only on this testcase.

---

## 4. Analysis

### 4.1 Why ML Produces Better Cut Costs

The multilevel approach works in three phases:

1. **Contraction** — The hypergraph is coarsened into smaller graphs by clustering connected modules. The contraction logs show three levels of net removal (1486 → 245 → 225 nets), indicating the graph was contracted at least 3 times.
2. **Initial partitioning** — FM is run on the smallest (coarsest) graph, where the problem is simpler and the optimizer can find a good global structure.
3. **Uncoarsening + refinement** — The partition is projected back up to the original graph, with FM refinement at each level.

This hierarchy helps the optimizer **escape local minima** that trap single-level FM. A greedy move in the full graph might appear bad due to local constraints, but the same structure at a coarsened level reveals the global benefit.

### 4.2 Why ML Is Slower

The runtime overhead comes from:

- **Graph contraction**: Computing minimum maximal matching, building clustered netlists, removing duplicate nets. This is O(nets × degree) per level.
- **Multiple FM passes**: FM optimization runs at each level of the hierarchy, not just once on the full graph.
- **Projection**: Mapping partitions up and down between hierarchy levels.

FM-only runs one optimization pass on the full 12K-module graph. ML runs optimization on 3+ increasingly smaller graphs, then refines on the way back up — resulting in roughly 2× total work.

### 4.3 Variance and Stability

| Metric          | FM-only | ML    |
|-----------------|---------|-------|
| Cut cost range  | 345–709 | 289–521 |
| Coefficient of Variation | 28.9% | 23.6% |

ML produces **more consistent results** across different random initial partitions. The contraction phase abstracts away noise from the initial random assignment, making the final quality less dependent on the starting point.

### 4.4 Tradeoff Summary

```
                  Cut Quality    Runtime
FM-only           ⚠️ Worse       ✅ Faster
ML (multilevel)   ✅ Better       ⚠️ 2× slower
```

The ML partitioner offers **~20% better cut quality at ~2× the runtime cost**. For VLSI CAD flows where partition quality directly impacts downstream placement/routing metrics, this tradeoff is almost always worthwhile.

---

## 5. Conclusion

On the ibm01 benchmark (12K modules, 14K nets), the **multilevel (ML) partition manager consistently outperforms the single-level FM-only partitioner**:

- **Cut cost**: 20.7% lower on average (375.6 vs 473.4)
- **Runtime**: 2.05× slower (29.97s vs 14.59s)
- **Consistency**: Lower variance across different initial partitions

The multilevel strategy of coarsen → partition → uncoarsen → refine is effective at finding better-quality solutions by avoiding local minima that trap flat FM optimization.

---

*Generated by benchmark_ibm01.py — run `python benchmark_ibm01.py` to reproduce.*
