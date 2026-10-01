# Tunable Parameters in `ckpttnpy`

A complete reference of every user-tunable parameter of the algorithms in this
project, together with its default value and source location.

## Key finding

`ckpttnpy` has **no central `Options` object**. The only `@dataclass` is
`FMPartSpec` (`src/ckpttnpy/FMPartSpec.py:23`), which is an internal frozen
product-family spec (GainCalc / GainMgr / ConstrMgr / PartMgr), not user tuning.
Tunables are spread across constructor parameters, module-level constants, and
CLI arguments. `bal_tol` (balance tolerance) and `num_parts` / `k` are the
dominant knobs.

---

## 1. Core partitioning tunables

| Parameter | Default | Location | Notes |
| --- | --- | --- | --- |
| `bal_tol` | required (no default) | `src/ckpttnpy/FMConstrMgr.py:51`, `MLPartMgr.py:22`, `FMPartSpec.py:33` | Balance tolerance; `lowerbound = round((1 - bal_tol) * totalweight / num_parts)` (`FMConstrMgr.py:60`). |
| `num_parts` / `k` | `2` | `FMConstrMgr.py:51`, `FMGainMgr.py:24`, `FMBiGainCalc.py:33`, `MLPartMgr.py:22` | Selects bi- vs k-way. |
| `module_weight` | `None` → unit weights | `FMConstrMgr.py:68` | `1 if module_weight is None`. |
| `LIMIT_SIZE` / `limitsize` | `50` | `MLPartMgr.py:27`; `partitioner.py:27` | Coarsening threshold. |
| `max_passes` (optimize loop) | `100` (hardcoded) | `PartMgrBase.py:131` | `for _ in range(100)` — not exposed. |
| contraction ratio | `> 3/2` reduction (hardcoded) | `MLPartMgr.py:65` | `hgr2.modules * 3/2 < hyprgraph.modules`. |

### Constraint / gain manager constructors

| API | Signature | Default |
| --- | --- | --- |
| `FMConstrMgr` | `(hyprgraph, bal_tol, module_weight, num_parts=2)` | `num_parts=2` |
| `FMGainMgr` | `(GainCalc, hyprgraph, num_parts=2)` | `num_parts=2`; gain bucket bound = `get_max_degree() * (num_parts - 1)` (`FMGainMgr.py:29`) |
| `FMBiGainCalc` | `(hyprgraph, _=2)` | `2` |
| `FMKWayGainCalc` | `(hyprgraph, num_parts)` | required |
| `FMKWayGainMgr` | `(GainCalc, hyprgraph, num_parts)` | required |

---

## 2. Multi-level managers

File: `src/ckpttnpy/MLPartMgr.py`, `src/ckpttnpy/partitioner.py`.

| Class / function | Signature | Default |
| --- | --- | --- |
| `MLPartMgr` | `(spec, bal_tol, num_parts=2)` | `num_parts=2` |
| `MLBiPartMgr` | `(bal_tol)` | `num_parts` fixed `2` |
| `MLKWayPartMgr` | `(bal_tol, num_parts)` | required |
| `MLBiNNPartMgr` | `(bal_tol)` | `num_parts` fixed `2` |
| `MLKWayNNPartMgr` | `(bal_tol, num_parts)` | required |
| `create_partitioner` | `(k, algo, bal_tol, limitsize=50)` | `limitsize=50` |
| `create_flat_part_mgr` | `(k, algo, bal_tol, hyprgraph, module_weight)` | required |

`algo` must be `"FM"` or `"NN"` (`partitioner.py:19-23`).

---

## 3. Clustering / duplicate-net detection

File: `src/ckpttnpy/min_cover.py`.

| Constant / parameter | Default | Location |
| --- | --- | --- |
| `LOW_PIN_NET_THRESHOLD` | `5` | `min_cover.py:23` |
| `MINHASH_SIG_SIZE` | `64` | `min_cover.py:24` |
| `MINHASH_SIMILARITY` | `0.8` | `min_cover.py:25` |
| `_minhash_signature(items, k=64)` | `k=64` | `min_cover.py:30` |
| High-pin minHash cutoff | `deg <= 200` (hardcoded) | `min_cover.py:244` |

---

## 4. Multi-FPGA

File: `src/ckpttnpy/MultiFPGAPartMgr.py`.

| Parameter | Default | Location |
| --- | --- | --- |
| `bal_tol` | `0.1` | `MultiFPGAPartMgr.py:24` |
| `MultiFPGAGainCalc(hyprgraph, num_parts=2)` | `2` | `MultiFPGAPartMgr.py:135` |
| `inter_fpga_cost_weight` | `1.0` | `MultiFPGAPartMgr.py:137` |
| `set_inter_fpga_cost_weight(weight)` | required | `MultiFPGAPartMgr.py:139` |

---

## 5. CLI options

File: `src/ckpttnpy/cli.py`.

| Option | Default | Location |
| --- | --- | --- |
| `k` (positional) | `2` | `cli.py:361, 435` |
| `epsilon` (positional) | `0.05` (values > 1 divided by 100) | `cli.py:363, 436, 444-445` |
| `--input-format` | auto-detect | `cli.py:367-372` |
| `--fixed` | none | `cli.py:373-377` |
| `--output` | stdout | `cli.py:380-381` |
| `--output-format` | `"hmetis"` | `cli.py:383-388` |
| `--quiet` | `False` | `cli.py:389-391` |
| `--preset` | `"default"` | `cli.py:394-400` |
| `--objective` | none (parsed, unused) | `cli.py:401-405` |
| `--mode` | `"recursive"` (`direct` = NN) | `cli.py:406-412` |
| `--threads` (number of starts) | `1` | `cli.py:413-419` |
| `--seed` | `0` (0 = random device) | `cli.py:422-428` |
| `--verbose` | `False` | `cli.py:429` |
| `--time-limit` | none (parsed, unused) | `cli.py:430` |
| `--max-quality` | none (parsed, unused) | `cli.py:431` |

### Presets (`cli.py:295-304`)

| Preset | `bal_tol` | `recursive` |
| --- | --- | --- |
| `default` | `0.03` | `True` |
| `quality` | `0.01` | `False` |
| `highest_quality` | `0.005` | `False` |
| `deterministic` | `0.03` | `True` |
| `large_k` | `0.03` | `True` |

---

## 6. Harness utilities

File: `src/ckpttnpy/harness.py`.

| Function | Signature |
| --- | --- |
| `make_init_part` | `(hyprgraph, k, rng)` |
| `random_init_part` | `(part, num_modules, num_parts, module_fixed, rng)` |
| `multi_start` | `(n_starts, run_fn)` |

Experiments default: `N_STARTS = 10` (`experiments/_common.py:24`).

## 7. Logging

File: `src/ckpttnpy/logging_config.py`.

`setup_logging(log_level=logging.INFO, log_file=None, format_string=None)`
(`logging_config.py:13-17`); the default format string is set at
`logging_config.py:35`.

---

## 8. Fixed values in tests, benchmarks, and experiments

| Source | Constant | Value |
| --- | --- | --- |
| `tests/test_MLPartMgr.py:13`, `tests/test_MLNNPartMgr.py:13`, `tests/test_MLPartMgr_ibm.py:28`, `tests/test_MLPartMgr_yosys.py:30` | `bal_tol` | `0.45` |
| same | `limitsize` | `7` / `10` |
| same | `random.seed` | `1234` / `42` |
| `tests/test_FMKWayPartMgr.py:30` | `bal_tol` | `0.45` |
| `tests/test_MultiFPGAPartMgr.py:33` | `bal_tol` | `0.1` |
| `benchmark_ibm01.py:16-20` | `SEED`, `NUM_RUNS`, `BAL_TOL`, `LIMITSIZE`, `K_VALUES` | `42`, `5`, `0.45`, `10`, `[2, 3, 5]` |
| `benchmarks/compare_fm_nn.py:20-22` | `BAL_TOL`, `LIMIT_SIZE`, `SEEDS` | `0.45`, `50`, `[0, 1, 2, 3, 4]` |
| `experiments/random_part:41` | `bal_tol` | `0.45` |
| `experiments/bipartition:29-33`, `experiments/partition3way:29-33` | `bal_tol` validation | error if `>= 0.5`, warn if `<= 0.3` |

---

## Summary of genuine tunables

| Tunable | Default | Location |
| --- | --- | --- |
| `bal_tol` | required (facade: `0.1` on MultiFPGA; CLI presets `0.03` / `0.01` / `0.005`) | `src/ckpttnpy/FMConstrMgr.py:51`, `MultiFPGAPartMgr.py:24`, `cli.py:297-303` |
| `num_parts` / `k` | `2` | `src/ckpttnpy/FMConstrMgr.py:51`, `MLPartMgr.py:22`, `cli.py:435` |
| `limitsize` / `LIMIT_SIZE` | `50` | `src/ckpttnpy/MLPartMgr.py:27`, `partitioner.py:27` |
| `max_passes` | `100` (hardcoded) | `src/ckpttnpy/PartMgrBase.py:131` |
| `module_weight` | `None` → unit weights | `src/ckpttnpy/FMConstrMgr.py:68` |
| `LOW_PIN_NET_THRESHOLD` | `5` | `src/ckpttnpy/min_cover.py:23` |
| `MINHASH_SIG_SIZE` | `64` | `src/ckpttnpy/min_cover.py:24` |
| `MINHASH_SIMILARITY` | `0.8` | `src/ckpttnpy/min_cover.py:25` |
| `inter_fpga_cost_weight` | `1.0` | `src/ckpttnpy/MultiFPGAPartMgr.py:137` |
| CLI `epsilon` / `--threads` / `--seed` / `--mode` / `--preset` | `0.05` / `1` / `0` / `recursive` / `default` | `src/ckpttnpy/cli.py:363, 417, 427, 410, 398` |
| `setup_logging(log_level)` | `logging.INFO` | `src/ckpttnpy/logging_config.py:14` |
| `multi_start(n_starts)` (experiments) | `N_STARTS = 10` | `experiments/_common.py:24` |

Everything else is problem data (hypergraph, module weights, fixed-module set,
initial partition) or a hardcoded constant. Three CLI flags — `--objective`,
`--time-limit`, `--max-quality` — are parsed but never used.
