# Circuit (Hypergraph) Partitioning

---

## Why?

Fundamental CAD Problem?

Partitioning based Placement

Hierachical Design

Multi-FPGA

---

## Problem

- Balanced partitioning
  NPO-hard (non-approximatable)
- Balanced tolerance factor: 3%, 10%

- Fixed cell

---

## Algorithms

Local search + Multi-level

- Fiduccia-Mattheyses partitioning
  - data structure: bucket priority queue
  - FIFO or LIFO ?
- Simulated Annealing

- Multi-level (Multi-Grid)
  hMetis/Metis
  V-Cycle
  W-Cycle

  Memory management - stop coarsening if memory is not enough

- Flow-based algorithm
  Max-flow Min-cut Theorem

Jason Cong - UCLA - MLPart
Andrew Kahng - UCLA -> UCSD OpenRoad
Martin Wong
