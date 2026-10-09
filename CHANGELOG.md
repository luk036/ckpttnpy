# Changelog

## Version 0.2 (2026-10-09)

### Features
- **Partitioner factory + product-family spec**: Introduced an `FMPartSpec` / product-family spec and a partitioner factory, and routed the benchmarks through the factory. (#da5c441, #ebb8a12)
- **FM benchmark + ibm03 testcases**: Added an FM benchmark script and the `ibm03` testcases. (#d7c9ef4)
- **Retuned partitioning defaults**: Retuned the defaults and fixed the `--preset` wiring. (#93ae408)
- **Shared harness + experiments**: Added a shared partition harness (`harness.py`) with a shared `make_init_part`, and collapsed the experiment scripts onto a shared base. (#6ff0445, #f586cec, #6ace1d5)

### Performance
- **~1.7× faster FM partitioning**: Cached the adjacency and skipped no-op moves. (#ba597a0)
- **Lower memory**: Fixed the `waitinglist` class-variable bug, reduced journal snapshots, and reused buffers. (#7108652)

### Bug Fixes
- **Balance lower bound**: Enforced the documented `(1-ε)W/k` balance lower bound. (#67647b1)
- **hMetis vertex ids**: Auto-detect 1-based hMetis vertex ids in the `.hgr` reader. (#2bfd33f)
- **mypy errors**: Resolved type annotations, unreachable code, and kwargs issues, and removed an unused snapshot variable. (#2568e8a, #528b7c6)

### Testing & Code Quality
- **Coverage raised 82% → 95%**: Excluded `cli.py` from coverage and added cross-port-parity tests. (#3d8b2a8, #test_cross_port_parity)
- **Deterministic tests**: Seeded the ML bi-NN test for determinism and shared `make_init_part` in the ML partition tests. (#83a6f5e, #f586cec)

### Code Cleanup
- **Removed dead code & boilerplate**: Dropped `NNGainMgr`, the PyScaffold skeleton, `GEMINI.md` / `IFLOW.md` / the duplicate `LICENSE`, and the Gemini AI agent workflows; moved flake8 config to `.flake8`; removed AI slop. (#b64d6c0, #ba1e902, #78f8cbc, #be4e683, #76ce53a, #cf51d11)
- **Refactors**: Made `NNPartMgr` a `PartMgrBase` subclass overriding only the pass, and trimmed the NNPartMgr docstrings. (#f483046, #07c0cb5)
- **Metadata**: Updated the description / url / project_urls. (#c905f2b)

### Documentation
- **Partitioning paper + Beamer talk**: Added `paper/ckpttn-paper.md` (861 lines) with figures and engineering notes and `paper/ckpttn-talk.md`, plus the FM-vs-NN benchmark report and a tunable-parameter reference. (#55303a4, #be7395c, #58c06b7, #a8c6a49, #6626ca1, #fd591be)
- **Design notes moved**: Moved the design notes into `paper/`. (#be7395c)

### Build & CI
- **Updated GitHub Actions** and removed the Gemini scheduled-triage and dispatch workflows. (#78f8cbc, #be4e683)
