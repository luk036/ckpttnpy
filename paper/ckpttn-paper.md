---
title: "ckpttn: Multilevel Circuit Partitioning"
author:
  - Wai-Shing Luk
documentclass: IEEEtran
classoption:
  - 10pt
bibliography: ckpttn.bib
csl: ieee.csl
nocite: |
  @*
header-includes: |
  \usepackage{graphicx}
keywords:
  - hypergraph partitioning
  - circuit partitioning
  - Fiduccia-Mattheyses
  - multilevel refinement
  - min-cut
abstract: |
  Balanced hypergraph partitioning is a fundamental step in VLSI physical
  design, and the Fiduccia-Mattheyses (FM) local search, refined inside a
  multilevel framework, is its workhorse. This paper describes ckpttn, an
  open-source   multilevel circuit partitioner built on three principles: certify small
  instances exactly with a middle-levels Gray-code enumeration, keep the FM
  machinery but make the gain bookkeeping cheap, and coarsen the hypergraph
  aggressively with a primal-dual minimum maximal matching and MinHash
  duplicate-net pruning. We state the partitioning problem, derive
  the FM gain updates and their bucket data structure, present a simpler greedy
  refiner for comparison, and describe a symmetry-reduced enumeration that
  visits every balanced bipartition.   On the p1, ibm01, and ibm03 benchmarks,
  multilevel refinement reduces the cut cost by 27-54 percent over flat FM, the
  greedy refiner is 8-35 times faster but 1.4-2.2 times worse, and the same
  algorithm behaves consistently across Python, C++, and Rust ports, whose inner
  loops are all organized around the observation that most gain updates are
  no-ops. The C++ port partitions the full ISPD98 suite, up to 210,000 modules,
  in under twenty seconds per instance. Unlike classical tools, ckpttn warns
  explicitly when the balance constraint cannot be met.
---

```{=latex}
\begin{IEEEkeywords}
hypergraph partitioning, circuit partitioning, Fiduccia-Mattheyses, multilevel refinement, min-cut.
\end{IEEEkeywords}
```

## Introduction

Circuit partitioning divides the cells of a netlist into a small number of
roughly equal parts while cutting as few connections as possible. It is the
first step of the physical-design flow and reappears throughout it: as the
driver of partitioning-based placement, as the basis of hierarchical design and
multi-FPGA mapping, and as a load-balancing primitive in parallel computing.
Because the number of cut nets directly limits routability and timing, even a
few percent of cut reduction is worth pursuing.

Partitioning has a four-decade history. The Kernighan--Lin (KL) heuristic
introduced pairwise interchange as a local search [@kernighan1970]; Schweikert
and Kernighan formalized the hypergraph (net) model still in use
[@schweikert1972]; and Fiduccia--Mattheyses (FM) replaced pairwise swaps with
single-module moves and a bucket priority queue, making one pass linear in the
netlist size [@fiduccia1982]. Move-based refinement was then extended to $k$-way
partitions [@krishnamurthy1984; @sanchis1989; @cong1998], while spectral methods
pursued the algebraic alternative [@fiedler1973; @pothen1990; @hagen1992] and
network-flow formulations [@yang1994; @liu1998] exploited the max-flow/min-cut
theorem. The multilevel paradigm -- coarsen, partition, then uncoarsen and
refine -- made FM scale to hundreds of thousands of modules
[@hendrickson1995; @karypis1997; @karypis1998; @karypis1999], and the ISPD98
benchmark suite standardized how partitioners are compared [@alpert1998]. The
resulting arc is surveyed by Alpert and Kahng [@alpert1995], Papa and Markov
[@papa2007], and Buluç et al. [@buluc2016].

This paper describes **ckpttn**, a compact, open-source multilevel partitioner.
Its design follows three principles.

1. **Certify small instances exactly.** Once a graph is small enough, a
   middle-levels Gray-code enumeration visits every balanced bipartition of it,
   turning the multilevel leaf from a heuristic into a certified optimum -- the
   only one of the three principles that guarantees an optimal solution.
2. **Keep FM, but make it cheap.** The Fiduccia-Mattheyses (FM) local search
   [@fiduccia1982] is retained as the refinement operator, but the gain updates
   are organized so that the common case -- a net that stays uncut after a move
   -- does no work, and the inner loop avoids gratuitous allocation and lookup.
3. **Coarsen aggressively.** Large instances are contracted through a
   primal-dual *minimum maximal matching*, with duplicate nets merged by a
   MinHash pre-filter, so that the expensive refinement runs on much smaller
   graphs.

The same algorithm is implemented in Python, C++, and Rust from one
specification, and it emits an explicit warning when the requested balance
cannot be achieved -- a guarantee that widely used tools do not make.

Work since then has pushed in three directions. Multilevel partitioners have
adopted $n$-level hierarchies, community-aware coarsening, and flow-based
refinement, culminating in KaHyPar [@schlag2016; @akhremtsev2017; @heuer2019;
@schlag2023] and its scalable shared-memory successor Mt-KaHyPar
[@gottesburen2021; @gottesburen2024]; the graph-partitioning system KaHIP
explored parallel and evolutionary refinement [@sanders2012].
Constraint-driven partitioners now target modern physical design: TritonPart
handles timing, multi-dimensional balance, and embedding constraints
[@bustany2023], SpecPart and K-SpecPart add supervised spectral embeddings
[@bustany2022; @bustany2024], and FPGAPart targets interposer-based multi-die
FPGAs [@iyer2025]. Finally, learning-based partitioning is emerging, with graph
neural networks evaluated on VLSI hypergraphs [@khan2024]. The same algorithms
serve the wider scientific-computing ecosystem through tools such as Mondriaan
[@vastenhouw2005] and Zoltan [@devine2002], and a recent survey
[@catalyurek2023] tracks the whole area.

## Problem Formulation {#sec:problem}

A circuit is modeled as a weighted hypergraph $H = (V, \mathcal{E})$. The
vertices $V$ are the modules (cells and I/O pads) and each hyperedge (net)
$e \in \mathcal{E}$ connects two or more vertices. A *$k$-way partition*
assigns every vertex to one of $k$ blocks $P_1, \ldots, P_k$ that are pairwise
disjoint and cover $V$. A net is *cut* if it has pins in more than one block.

The objective is to minimize the total weight of the cut nets,

$$
\min \sum_{e \in \mathcal{E}} w(e) \cdot \mathbb{1}[\, e \text{ is cut} \,],
$$

subject to a balance constraint on the block weights. With $m(v)$ the module
weight and $W = \sum_{v \in V} m(v)$ the total weight, each block must satisfy

$$
(1-\epsilon)\,\frac{W}{k} \;\le\; \sum_{v \in P_i} m(v) \;\le\;
(1+\epsilon)\,\frac{W}{k}, \qquad i = 1, \ldots, k,
$$

where the *imbalance factor* $\epsilon$ controls how much imbalance is
tolerated. Small $\epsilon$ (say $0.01$) makes the problem much harder; a loose
$\epsilon$ makes it nearly unconstrained. A few modules may also be *fixed* to
a prescribed block (for example, I/O pads), in which case they can never move.
Balanced partitioning is NP-hard [@kahng2011; @sherwani1999], and for tight
tolerance the multilevel method is the practical method of choice.

The choice of method tracks the instance, and it is worth stating the map
explicitly. A netlist that is close to a mesh is handled well by spectral
bisection [@pothen1990; @hagen1992]; an instance whose balance can be relaxed is
a candidate for a network-flow formulation built on the max-flow/min-cut theorem
[@yang1994; @liu1998]; a graph of at most a few tens of modules can be solved
exactly by the enumeration of Section III-A; and beyond that the multilevel
method [@karypis1998] is preferred when the balance tolerance is tight, while
single-level FM [@fiduccia1982] suffices when it is loose.
ckpttn exposes the extremes of this map through its presets (Section IV), and
the two refiners of Section III are the local-search policies that sit inside
the multilevel loop.

## Algorithms

We begin with the exact method, because it is the only one that *certifies*
optimality. It is practical only on small graphs, so the local-search refiners
and the multilevel framework that follow are what make large instances
tractable; the exhaustive leaf is applied to the coarsest level of that
framework.

### Exhaustive Refinement by Middle-Levels Gray Code {#sec:gray}

A balanced bipartition of the coarsest graph can be *enumerated*. Consider
assigning each module one bit, $0$ for block A and $1$ for block B. A balanced
partition is a bitstring with exactly $n$ or $n+1$ ones. The *middle-levels
graph* $G_n$ of the $(2n+1)$-dimensional hypercube has as vertices all bitstrings
of weight $n$ or $n+1$, with edges between bitstrings that differ in exactly one
bit. A Hamiltonian cycle of $G_n$ therefore visits every balanced bipartition
exactly once, and each transition is a single module flip -- a single FM move.
The existence of such a cycle for every $n \geq 1$ was conjectured in 1982 and
proved constructively only recently [@mutze2016; @gregor2018]; the construction
is memoryless and recursive, and related Gray-code perspectives are surveyed by
Savage [@savage1997].

Because a flip touches only the nets incident to one module, the incremental
cost update is $O(\deg)$ per step, and the enumeration visits

$$
2\binom{2n+1}{n} = \binom{L}{n} + \binom{L}{n+1}
$$

states for $L$ bits. The size grows quickly -- $924$ states for $n = 11$,
$705{,}432$ for $n = 20$ -- so the enumeration is used only at the coarsest
level, where the contracted graph has at most a few tens of modules. There it
yields a certified optimum for that level, which the uncoarsening then refines
heuristically. The same constructive techniques were later extended to the
sparser Kneser graphs [@mutze2018].

The construction is memoryless and is organized around a binary tree that
encodes the Dyck-path structure of the current bitstring; two recursively
defined flip sequences, one per direction of travel, advance the cycle, so the
whole traversal is a sequence of single-bit flips. For a balanced bipartition of
$N$ modules each of the first $N$ bits is one module's block assignment; when
$N$ is even a single dummy bit is appended so that the bitstring has odd length
$L = N + 1$, and the flips that touch the dummy bit are ignored. The leaf
threshold follows from the measured cost of the traversal -- instant to
$n = 11$, about $0.2$ s at $n = 20$, and a few seconds at $n = 25$ ($10.4$ M
states) -- so the enumeration is kept to the coarsest level, where it certifies
the optimum.

### Fiduccia-Mattheyses Refinement {#sec:fm}

FM is a local search over a fixed partition. It repeatedly moves a single
module, always the one whose move improves the objective most, and, following
Kernighan--Lin [@kernighan1970], it accepts worsening moves within a pass so
that it can escape shallow local minima. The
quantity that drives the search is the *gain* of a move, i.e. the reduction in
the cut cost,

$$
g(v) = FS(v) - TE(v),
$$

where $FS(v)$ (from-side) counts the nets that touch $v$ and lie entirely in
$v$'s current block, and $TE(v)$ (to-side) counts the nets that touch $v$ and
lie entirely in the destination block. A positive gain means the cut shrinks.

Because FM considers one move at a time, the relevant quantity after a move is
the change in the gain of the moved module's neighbours. For a 2-pin net the
update is a simple $\pm 1$ or $\pm w(e)$; for a 3-pin net a short case analysis
suffices; a general net only changes a neighbour's gain when the net has at
most one pin on one side, so the common case (two or more pins on each side)
yields a zero delta. Detecting and skipping that zero is the single most
profitable optimization in the whole partitioner.

The candidate moves are kept in a *bucket* priority queue keyed by gain. With
integer gains the queue supports insertion, extraction of the maximum, and a
key update in $O(1)$ amortized time, which is what makes FM a linear-time
heuristic in practice [@fiduccia1982]. One *pass* is:

1. initialize the gains of every unlocked module and build the buckets;
2. repeatedly select the highest-gain legal move, execute it, and mark the
   module *locked* (a locked module cannot move again in this pass), then
   update the gains of its neighbours;
3. if the queues become empty, or no legal move remains, restore the best
   partition seen during the pass and start the next pass.

Restoring the best state is done with a snapshot, a re-application of the moves,
or a roll-back of the moves; ckpttn uses snapshots for the general path and can
skip the snapshot entirely when no improving move was found. Passes continue
until the cost stops decreasing.

Two properties keep the inner loop cheap. The work done by a move is
proportional to the degrees of the incident nets, $\sum_{e \ni v} \deg(e)$, not
to the size of the graph; and the candidate set is a bounded priority queue, so
with integer gains insertion, maximum extraction, and key update are $O(1)$
amortized. Three pieces of machinery distinguish FM from a plain greedy descent:
the bucket queue that makes the best move cheap to find, the per-pass locking
that keeps a module from moving twice, and the snapshot/roll-back that makes the
temporarily worsening moves safe to take. Remove all three and one obtains the
simpler refiner of the next subsection.

### A Simpler Refiner {#sec:nn}

The bucket-and-lock machinery exists to *escape* local minima. If one is willing
to accept a worse local optimum, a pure greedy refiner is much cheaper: take the
highest-gain move while its gain is positive, with no snapshotting, no rollback,
and no locking. We call this the *NN* (no-nonsense) refiner. It monotonically
descends to the nearest local optimum, and in return it is 8-35 times faster
than FM on flat graphs. The multilevel framework closes most of the quality gap,
which is precisely the intended role of a cheap refiner inside the coarsen/
refine loop.

NN is not a separate program but a different policy inside the same pass
skeleton. The base class owns the loop -- select the maximum-gain move, ask the
constraint manager whether it is legal, apply it, update the gains of the
neighbours -- and exposes a single overridable hook for one pass. FM's hook adds
the locking and the roll-back; NN's hook stops at the first non-positive gain.
This is the Template Method pattern for the skeleton and the Strategy pattern
for the gain and constraint managers, and it is what lets one gain calculator
serve the flat, multilevel, and k-way partitioners. Termination of NN is
immediate from monotonicity: the cut is a non-negative integer and every
accepted move is strictly improving, so the descent cannot cycle and must stop
at a local optimum -- no locking and no snapshot are required. All three ports
implement the same hook with the same threshold, $g_{\max} \le 0$; a zero-gain
move is not taken, because without locking it could cycle.

### The Multilevel Framework {#sec:ml}

Flat FM is slow on graphs with hundreds of thousands of modules and is sensitive
to the initial partition. The multilevel method
[@hendrickson1995; @karypis1997; @karypis1998; @karypis1999; @caldwell2000]
removes both problems by solving a hierarchy of successively smaller graphs:

1. **Coarsen.** Contract the hypergraph: find a *maximum matching* of nets that
   share no module, replace each matched group by a single cluster whose weight
   is the sum of its members, and add up the weights of any nets that become
   identical. Repeat until the graph is small.
2. **Initial partition.** Partition the coarsest graph. Because it is small,
   this step can afford an expensive method (Section III-A).
3. **Uncoarsen and refine.** Project the partition back to the next finer graph
   and refine it -- with FM or NN -- at every level on the way up.

The matching is *minimum maximal*: it is maximal (no further net can be added
without overlap) and, among maximal matchings, of minimum total weight. It is
computed by a primal-dual 2-approximation that maintains a *gap* per net and
selects the tightest net in each uncovered neighbourhood. Pairing lighter nets
keeps the clusters small and preserves the structure that the refinement can
exploit. Duplicate nets (nets with the same module set) are merged; for
low-degree nets this is checked exactly, and for larger nets a 64-element
MinHash signature [@broder1997] pre-filters clearly dissimilar pairs (estimated
Jaccard similarity below $0.8$), so that the expensive exact comparison is
rarely needed.

Concretely, one contraction step is a five-stage pipeline: compute the
min-maximal matching and split the nets into matched clusters and remaining
nets, with the unmatched modules forming the cell list; build an intermediate
bipartite graph between the cells and the clusters; purge duplicate nets,
merging their weights and dropping the self-loops that clustering creates;
reconstruct the graph with remapped net indices; and wrap the result in a
hierarchical netlist. The hierarchical netlist carries the two projection maps
that make the rest of the method work -- a node-up map from an original module
to its contracted representative, used while coarsening, and a node-down map
from a cluster back to one of its members, used while refining. Duplicate
detection compares nets of degree at most five exactly and pre-filters larger
nets (up to degree 200) with the MinHash signature, falling back to the exact
comparison only above the $0.8$ similarity threshold.

A recursion guard keeps the contraction honest: a level is contracted only when
the result is materially smaller than its parent, $|V^{+}| \cdot 1.5 < |V|$.
Without the guard, a pathological instance can spend a dozen levels shrinking by
a few percent each time, as observed on ibm01.

### K-Way Partitioning

For $k > 2$ the search is organized as a sequence of pairwise refinements
[@sanchis1989; @cong1998]. Because the exhaustive leaf is inherently two-way,
each pair of blocks
$(i, j)$ is optimized in turn: the modules currently in block $i$ or $j$ are
isolated as the movable set (everything else is treated as fixed), the
middle-levels enumeration is run on that pair with the full netlist so that
cross-block pins are counted correctly, and the best pair partition is applied.
Pairs whose movable set is trivial or larger than a threshold are skipped, since
the enumeration is exponential in the number of movable modules. This pairwise
sweep is repeated a bounded number of times, and a flat FM legalization keeps
the block weights within tolerance between sweeps.

The leaf budget scales with the number of blocks: for $k$ parts the enumeration
is allowed $25k/2$ movable modules, spread over the $\binom{k}{2}$ pairs, so each
pair sees at most about fifteen modules on average and any pair whose movable
set exceeds that is skipped. For $k = 2$ this is the $25$-module limit of
Section III-A; for $k = 6$ it is $75$ modules over fifteen pairs, which
still leaves every pair's enumeration trivial. The enumeration runs on the full
netlist rather than on the isolated pair, so pins that land outside the pair are
still counted; this is what makes the pair's value a correct $k$-way cost rather
than an internal two-way cost.

## Implementation {#sec:impl}

**Architecture.** The partitioner is decomposed into four collaborating
objects, which are instantiated with a shared hypergraph:

- a *gain calculator* that computes gains and their updates, specialized by net
  degree (2-pin, 3-pin, and general nets, with a high-degree cutoff);
- a *gain manager* that owns the bucket queues and performs select, lock, and
  key-update;
- a *constraint manager* that decides whether a move is legal, tracking the
  block weight difference from the ideal;
- a *partition manager* that runs the pass loop, takes snapshots, and restores
  the best state.

Separating these concerns lets the same gain calculator be reused for the flat,
multilevel, and k-way managers. The arrangement is the Template Method pattern
for the pass skeleton -- the base class fixes the sequence of select, legalize,
apply, and update, and the subclass supplies only the per-pass hook -- together
with the Strategy pattern for the gain, constraint, and partition managers,
which can be swapped without touching the loop.

**Ports.** The same algorithm is implemented in Python (`ckpttnpy`), C++
(`ckpttn-cpp`), and Rust (`ckpttn-rs`). The Python reference uses NetworkX; the
C++ port uses a hand-rolled hypergraph and templates; the Rust port uses
`petgraph`. Cross-language regression tests check that a small hand-built
partition yields the same cut in all three.

In the Python reference the collaboration is spread over a small set of modules:
`FMBiGainCalc` and `FMKWayGainCalc` compute the gains, `FMBiGainMgr` and
`FMKWayGainMgr` own the buckets, `FMBiConstrMgr` and `FMKWayConstrMgr` decide
legality, `PartMgrBase` fixes the pass skeleton, `FMPartMgr` and `NNPartMgr` are
its two policies, `MLPartMgr` drives the hierarchy, `HierNetlist` holds the
projection maps, and `min_cover` performs the contraction.

**Interface.** A command-line front end partitions a hypergraph file directly:

```
ckpttnpy circuit.hgr <k> <epsilon>
```

with options for the input format (hMetis, JSON, DIMACS), fixed modules, output
format, a preset, the objective (cut, $km1$, sum of external degrees, or $km1a$),
the mode (direct or recursive bisection), the number of parallel starts, and the
random seed. Presets bundle the balance tolerance and mode:

```{=latex}
\begin{table}[t]
\centering
\textbf{Presets: balance tolerance and partitioning mode.}\par
\begin{tabular}{lll}
\hline
Preset & Balance & Mode \\
\hline
\texttt{default}          & 3\%   & recursive \\
\texttt{quality}          & 1\%   & direct \\
\texttt{highest\_quality} & 0.5\% & direct \\
\texttt{deterministic}    & 3\%   & recursive (fixed seed) \\
\texttt{large\_k}         & 3\%   & recursive \\
\hline
\end{tabular}
\end{table}
```

**Tuning.** The presets are thin wrappers over a small set of constants, most of
which are fixed at compile time rather than exposed as options. Contraction is
attempted while the graph has at least \texttt{limitsize} modules (50 in the C++
port, size-adaptive $\max(50, \lvert V \rvert / 6)$ in Python); gain updates are
skipped on nets of degree above 500; the bucket buffers are sized 32768 for
bi-partitioning and 65536 for k-way; and degree-2 and degree-3 nets take a
specialized fast path. On the coarsening side, nets of degree at most 200 are
compared exactly for duplication, while the 64-element MinHash pre-filter
(Jaccard threshold $0.8$) only engages if that threshold is lowered. Several starts can
be run in parallel: with $t$ starts and a seed $s$ the runs use seeds
$s + i \cdot 104729$, so the search is reproducible while still exploring
different basins; on ibm02 (19,601 modules) the best single start cost 282 cut
nets, whereas four deterministic starts reached 87.

```{=latex}
\begin{table*}[t]
\centering
\textbf{Selected constants of ckpttn.}\par
\begin{tabular}{lll}
\hline
Constant & Value & Role \\
\hline
\texttt{limitsize}                   & 50            & coarsen while $|V| \ge$ this (C++); Python auto $\max(50, |V|/6)$ \\
\texttt{FM\_MAX\_DEGREE}             & 500           & skip gain updates above this degree \\
\texttt{stack\_buf\_size}            & 32768 / 65536 & bounded-queue buffers (bi / k-way) \\
\texttt{special\_handle\_2pin\_nets} & true          & degree-2/3 fast path \\
\texttt{LOW\_PIN\_NET\_THRESHOLD}    & 200           & exact duplicate check at this degree \\
\texttt{MINHASH\_SIG\_SIZE}          & 64            & MinHash signature length \\
\texttt{MINHASH\_SIMILARITY}         & 0.8           & Jaccard pre-filter threshold \\
\texttt{MINHASH\_MAX\_DEGREE}        & 200           & skip MinHash above this degree \\
\hline
\end{tabular}
\end{table*}
```

**Balance warning.** If the requested balance is impossible -- for instance,
because a single module outweighs an entire block -- ckpttn reports the failure
in its final output. On a five-module instance whose largest module has weight
$10^{7}$ and whose ideal block weight is about $5 \times 10^{6}$, the block
weights are $10^{7}$ and $4$ and ckpttn prints an explicit warning that the
balance constraint is violated, whereas other tools return the same result
silently.

**Inner loop.** Because FM is dominated by the per-move key update, the ports
are engineered around the observation that most updates are no-ops. For a
general net with at least two pins on each side, moving one pin leaves every
neighbour's gain unchanged, so the update is skipped with a single test instead
of a queue operation; in the Python reference this cuts `modify_key` calls on
ibm03 from 7.37 M to 374 K. Two further layers of indirection were removed on
the Python side -- the NetworkX view objects and the adapter frames around
vertex and net lookup -- and the adjacency and degrees are now materialised once
per gain calculator into plain lists, which together take p1 from 299 ms to
216 ms and ibm03 from 14.6 s to 8.8 s for identical cuts. The C++ port replaced
a freshly allocated gain-change vector per move with a per-calculator buffer
returned as a `std::span`, which halves the k-way kernel on ibm03; the Rust port
removed a clone of the index vector and a `collect` of the neighbours per move,
both borrow-checker artifacts, for a uniform 28 percent win. Every change is
behaviour-preserving, verified by re-running against the same cut costs, which
is the only reason such micro-optimisations are admissible in a reference
implementation.

## Experimental Results {#sec:results}

All measurements below are wall-clock times on one host and are intended for
relative comparison; the Python numbers in particular are interpreter-bound.
Cut costs are hyperedge-cut values (lower is better). Two small benchmarks are
used throughout: p1 (833 modules, 902 nets) and ibm03 (23,136 modules, 27,401
nets, IBM-PLACE format); ibm01 (12,752 modules, 14,111 nets) is added for the
multilevel study. Random starts use a fixed SplitMix64 stream [@steele2014] so
that a seed denotes the same assignment in every port. The set is deliberately
small so that every port can be run repeatedly under identical conditions;
Section V-E adds a separate scaling study on the full ISPD98 suite. Unless
stated otherwise, the refiners in Tables I--IV use a $3$\% balance tolerance.

```{=latex}
\begin{figure*}[t]
\centering
\includegraphics[width=0.47\textwidth]{figs/p1-2way.pdf}\hfill
\includegraphics[width=0.47\textwidth]{figs/p1-3way.pdf}
\caption{Two-way (left) and three-way (right) partitions of the p1 benchmark
(833 modules, 902 nets), drawn on the bipartite module--net graph with modules
colored by block.}
\label{fig:p1}
\end{figure*}
```

### Refiners, Flat and Multilevel

Table I compares the FM and NN refiners, flat and multilevel, for
bi-partitioning at a $3$\% balance tolerance. Three trends are visible. FM
dominates quality: NN is 1.4-2.2 times worse in cut cost. NN dominates speed:
flat NN is 8-35 times faster (0.03 s versus 0.23 s on p1; 0.76 s versus 10.31 s
on ibm03). And the multilevel framework helps both, but helps NN far more --
coarsening recovers much of FM's quality (flat NN 231 to multilevel NN 106 on
p1; 7454 to 4081 on ibm03), which is exactly why a cheap refiner is useful
inside the loop.

The same ordering holds for three-way partitioning. On p1 the mean cut is
$347.2$ for flat NN and $164.0$ for multilevel NN, against $178.2$ and $121.8$
for FM; on ibm03 it is $12{,}278$ and $7{,}691$ for NN against $6{,}809$ and
$3{,}825$ for FM. Fig. 2 shows the full sweep over both benchmarks and all three
ports, and Fig. 3 isolates the two effects at work: how much the multilevel
framework buys over flat refinement, and how much worse NN is than FM.

```{=latex}
\begin{figure*}[t]
\centering
\includegraphics[width=\textwidth]{figs/fig_cut.pdf}
\caption{Mean cut cost of the FM and NN refiners, flat and multilevel, for
two-way and three-way partitioning of p1 and ibm03, in the three ports. Lower is
better; note the logarithmic scale.}
\label{fig:cut}
\end{figure*}

\begin{figure*}[t]
\centering
\includegraphics[width=0.48\textwidth]{figs/fig_gain.pdf}\hfill
\includegraphics[width=0.48\textwidth]{figs/fig_ratio.pdf}
\caption{Left: cut reduction of the multilevel framework over flat refinement
(p1, mean). Right: NN penalty, the ratio of NN to FM mean cut, with the parity
line shown.}
\label{fig:gainratio}
\end{figure*}
```

```{=latex}
\begin{table*}[t]
\centering
\caption{Refiners on p1 (833 modules) and ibm03 (23,136 modules), bi-partitioning at a $3\%$ balance tolerance, Python reference: best and mean cut over five seeds, and median wall-clock time.}
\label{tbl:fmnn}
\begin{tabular}{llrrrr}
\hline
Benchmark & Refiner & Multilevel & Best cut & Mean cut & Median time (s) \\
\hline
p1      & FM & no  & 99   & 105.4  & 0.23 \\
p1      & FM & yes & 68   & 77.4   & 1.01 \\
p1      & NN & no  & 212  & 231.4  & 0.03 \\
p1      & NN & yes & 85   & 106.0  & 0.80 \\
ibm03   & FM & no  & 3054 & 4021.2 & 10.31 \\
ibm03   & FM & yes & 1517 & 1840.2 & 44.69 \\
ibm03   & NN & no  & 7105 & 7453.8 & 0.76 \\
ibm03   & NN & yes & 3701 & 4081.0 & 52.99 \\
\hline
\end{tabular}
\end{table*}
```

### Multilevel versus Flat FM

Table II isolates the effect of the multilevel framework on ibm01 with
$k = 2$ and a balance tolerance of $3$\% at a limitsize of 2000, over five
seeds. Multilevel refinement lowers the cut on every run; the average reduction
is 44 percent, at a cost of about three times the runtime.

```{=latex}
\begin{table}[t]
\centering
\caption{Multilevel versus flat FM on ibm01 (12,752 modules, $k=2$, $3\%$ balance tolerance).}
\label{tbl:mlfm}
\begin{tabular}{lrrr}
\hline
Metric & FM-only & Multilevel & Change \\
\hline
Mean cut       & 1377.6 & 772.4  & $-43.9\%$ \\
Best cut       & 949    & 385    & $-59.4\%$ \\
Worst cut      & 1830   & 1192   & $-34.9\%$ \\
Mean time (s)  & 6.59   & 19.49  & $2.96\times$ \\
\hline
\end{tabular}
\end{table}
```

The reduction in variance is as important as the reduction in the mean: the
one-standard-deviation spread falls from 345 to 278 cut nets, because the
contraction absorbs the noise of the random initial partition.

### Cross-Language Behaviour

Table III reports the optimize time of the three ports on the same two
benchmarks in their release builds. The compiled ports are one to two orders of
magnitude faster than the interpreted one; the C++/Rust gap is an implementation
detail (the Rust port stores adjacency as a vector-of-vectors and pays a
per-call dispatch through an iterator trait), not an algorithmic one, and it
narrows as the graph grows.

```{=latex}
\begin{figure*}[t]
\centering
\includegraphics[width=\textwidth]{figs/fig_runtime.pdf}
\caption{Median wall-clock time of the three ports on the multilevel
configurations, p1 and ibm03 (logarithmic scale).}
\label{fig:runtime}
\end{figure*}
```

```{=latex}
\begin{table*}[t]
\centering
\caption{Optimize time of the three ports (release builds) on p1 and ibm03.}
\label{tbl:lang}
\begin{tabular}{lrrrr}
\hline
Benchmark & C++ (ms) & Rust (ms) & Python (ms) & C++ / Python \\
\hline
p1 (833 modules, 902 nets)        & 3.42 & 51.2 & 202   & $59\times$ \\
ibm03 (23{,}136 modules, 27{,}401 nets) & 262  & 1467 & 9691  & $37\times$ \\
\hline
\end{tabular}
\end{table*}
```

### Exhaustive Leaf

Table IV shows the cost of the middle-levels enumeration as a function of
the number of modules at the coarsest level. It is instant up to about twenty
modules and remains practical to roughly twenty-five; beyond that the
exponential growth dominates and the leaf falls back to FM.

```{=latex}
\begin{table*}[t]
\centering
\caption{Middle-levels Gray-code enumeration: states visited and time.}
\label{tbl:gray}
\begin{tabular}{rrr}
\hline
Modules $n$ & States & Time \\
\hline
11 & 924        & $<1$ ms \\
15 & 12{,}870   & $<1$ ms \\
20 & 705{,}432  & 0.20 s \\
25 & 10.4 M     & 3.4 s \\
\hline
\end{tabular}
\end{table*}
```

### Scaling to Large Instances

All measurements so far use instances of at most 23,136
modules. To probe the behaviour at the scale of a modern netlist, we ran the
C++ port on the complete ISPD98 suite [@alpert1998], whose 18 circuits range
from 12,752 to 210,613 modules. Table VI reports wall-clock time at $k = 2$,
balance $3$\%, and one start. Runtime grows close to linearly with size: $0.52$ s on ibm01 and
$19.1$ s on ibm18, a $16.5\times$ increase in modules for a $37\times$ increase
in time, so the multilevel loop stays practical well beyond the sizes of
Tables I--III. Peak resident memory is $227$ MB on ibm10 (69,429 modules) and
$557$ MB on ibm18 (210,613 modules), roughly $2.6$ KB per module.

These numbers must be read with care. The freely available ISPD98 files in
hMetis format do not pin the benchmark's fixed I/O pads, and the tool reports
cut in a unit that is not directly comparable to the published leaderboards for
this suite [@bustany2022; @bustany2023; @bustany2024]; omitting the
fixed-vertex constraints changes the problem and produces cut values that look
far better than the best published results. We therefore use this sweep only as
a runtime and memory scaling study and draw no cut-quality conclusion from it; a
like-for-like comparison against the state of the art is left to future work
(Section V-H).

With the balance constraint corrected (Section V-H), a like-for-like comparison
is possible. Table V runs all three tools single-threaded at $k = 2$ and
$\epsilon = 3$\% on three unit-weight ISPD98 files and reports the cut, the
wall-clock time, the imbalance $\max_i w_i k / W - 1$, and whether the balance
constraint holds. ckpttn's cut is $2.2$--$4.6\times$ larger than
Mt-KaHyPar's and $2.1$--$4.1\times$ larger than hMetis's [@karypis1999], and it
is the slowest of the three. Its one strength is balance: it stays below $1$\% on every
instance, whereas hMetis exceeds the requested $3$\% on ibm01 ($4.8$\%,
UBfactor $3$) and ibm10 ($3.9$\%) --- a silent violation that only becomes
visible when the returned partition is evaluated directly, which is exactly the
failure mode Section V-G is designed to expose. On this evidence the tool is
not competitive with the state of the art on cut or runtime; its contribution
is the cross-language reproduction and the diagnostic behaviour of
Section V-G.

```{=latex}
\begin{table*}[t]
\centering
\caption{Single-threaded head-to-head at $k=2$, $\epsilon=3\%$ on unit-weight ISPD98 files: one run per tool (ckpttn C++ port, seed 42; hMetis 1.5.3, UBfactor 3; Mt-KaHyPar 1.6.1, seed 42). Imbalance is $\max_i w_i k/W - 1$; balanced means at most $3\%$.}
\label{tbl:h2h}
\begin{tabular}{lrrrc}
\hline
Tool & Cut & Time (s) & Imbalance & Balanced \\
\hline
\multicolumn{5}{l}{\emph{ibm01 (12{,}752 modules)}} \\
ckpttn     & 973  & 0.52 & 0.86\%    & Yes \\
hMetis     & 240  & 0.13 & 4.82\%    & No \\
Mt-KaHyPar & 212  & 0.28 & 2.54\%    & Yes \\
\hline
\multicolumn{5}{l}{\emph{ibm03 (23{,}136 modules)}} \\
ckpttn     & 2169 & 0.92 & 0.83\%    & Yes \\
hMetis     & 1012 & 0.32 & 0.72\%    & Yes \\
Mt-KaHyPar & 993  & 0.64 & 0.45\%    & Yes \\
\hline
\multicolumn{5}{l}{\emph{ibm10 (69{,}429 modules)}} \\
ckpttn     & 4027 & 3.70 & 0.94\%    & Yes \\
hMetis     & 1276 & 1.01 & 3.87\%    & No \\
Mt-KaHyPar & 1509 & 1.44 & $<0.01$\% & Yes \\
\hline
\end{tabular}
\end{table*}
```

```{=latex}
\begin{table*}[t]
\centering
\caption{Scaling of the C++ port on the ISPD98 suite ($k=2$, balance $3\%$, one start, seed 42).}
\label{tbl:scale}
\begin{tabular}{lrrr}
\hline
Instance & Modules & Nets & Time (s) \\
\hline
ibm01  & 12{,}752  & 14{,}111  & 0.52 \\
ibm02  & 19{,}601  & 19{,}584  & 0.71 \\
ibm03  & 23{,}136  & 27{,}401  & 0.99 \\
ibm04  & 27{,}507  & 31{,}970  & 1.17 \\
ibm05  & 29{,}347  & 28{,}446  & 1.77 \\
ibm06  & 32{,}498  & 34{,}826  & 1.34 \\
ibm07  & 45{,}926  & 48{,}117  & 2.33 \\
ibm08  & 51{,}309  & 50{,}513  & 2.50 \\
ibm09  & 53{,}395  & 60{,}902  & 2.02 \\
ibm10  & 69{,}429  & 75{,}196  & 3.79 \\
ibm11  & 70{,}558  & 81{,}454  & 5.23 \\
ibm12  & 71{,}076  & 77{,}240  & 3.51 \\
ibm13  & 84{,}199  & 99{,}666  & 5.85 \\
ibm14  & 147{,}605 & 152{,}772 & 11.18 \\
ibm15  & 161{,}570 & 186{,}608 & 11.52 \\
ibm16  & 183{,}484 & 190{,}048 & 12.64 \\
ibm17  & 185{,}495 & 189{,}581 & 11.66 \\
ibm18  & 210{,}613 & 201{,}920 & 19.09 \\
\hline
\end{tabular}
\end{table*}
```

### The Cost of k-Way Partitioning

Table VII isolates the $k$-way cost on ibm10. The pairwise organization of the
search (Section III-E) makes the work grow much faster than the number of
blocks: $k = 2$ takes $4.3$ s, $k = 4$ about $16$ s, and $k = 8$ takes
$413$ s, a $97\times$ slowdown for a fourfold increase in $k$. This is
consistent with the $\binom{k}{2}$ pairwise sweeps, each of which may invoke the
exact leaf, and it is the clearest scalability limit of the current design.

```{=latex}
\begin{table}[t]
\centering
\caption{$k$-way cost on ibm10 (69{,}429 modules), C++ port, balance $3\%$, one start.}
\label{tbl:kway}
\begin{tabular}{rr}
\hline
$k$ & Time (s) \\
\hline
2 & 4.25 \\
3 & 16.2 \\
4 & 15.9 \\
8 & 413 \\
\hline
\end{tabular}
\end{table}
```

### Correctness and Warnings

Because the multilevel pipeline is intricate, correctness is checked by
cross-validation rather than by the cut cost alone: the ports share a SplitMix64
seed stream and hand-built instances whose cut is known, and the Rust port
carries a regression that asserts the multilevel result is non-trivial. The
explicit balance warning closes the remaining failure mode -- a silently
infeasible partition -- and makes the tool's output accountable in an automated
flow.

The test surface reflects the same three ports. The reference and its CLI carry
78 tests (25 for the interface and 53 for the algorithm); the C++ suite has 65
cases over the flat, multilevel, and Yosys paths plus the exhaustive leaf; and
the Rust port runs 245 tests plus a multilevel regression that asserts a
non-trivial result. Cross-port benchmarks re-use the same SplitMix64 stream, so
a reported seed denotes the same initial partition in every implementation.

### Limitations and Threats to Validity

We state the scope of these results plainly, since several conclusions are
weaker than they may first appear.

*Balance under tight tolerance (fixed).* The constraint manager originally
computed its lower bound as $\mathrm{round}(2W\varepsilon/k)$ rather than the
documented $(1-\varepsilon)W/k$, so a block was allowed to shrink to a fraction
$\varepsilon$ of the total; at $\epsilon = 3$\% this produced balance-violating
partitions (p1: 54/779). All three ports now use
$\mathrm{round}((1-\varepsilon)W/k)$; at $\epsilon = 3$\% p1 splits 406/427 and
the ISPD98 runs of Table V are balanced. The pre-fix numbers in Tables I--IV
are being regenerated at the corrected constraint.

*Scale.* Tables I--III use instances of at most 23,136 modules and are
interpreter-bound; Table VI extends the runtime and memory study to 210,613
modules, but we have not tested the million-gate designs (for example the
Titan23 suite) that motivate the parallel partitioners.

*Limited head-to-head.* Table V compares ckpttn directly against hMetis and
Mt-KaHyPar, but it is a single run per tool on three instances at one tolerance,
so the run-to-run variation (notably of hMetis) is not characterised. It does
not cover the constraint-driven objectives of SpecPart or TritonPart
[@bustany2022; @bustany2023]. It confirms that the "competitive with mature
tools" phrasing of earlier drafts is not supported: ckpttn's cut is
$2$--$5\times$ larger than both baselines.

*Benchmark comparability.* Even the scaling study above cannot be read as a
quality result, because the free ISPD98 files we used omit the fixed-I/O-pad
convention of the benchmark and the cut unit differs from the published
leaderboards [@bustany2022; @bustany2023; @bustany2024].

*Exact leaf.* The middle-levels enumeration is exponential and is used only at
the coarsest level, below roughly 25 modules (Table IV). The certified optimum
is therefore an optimum of a small, contracted graph; it cannot undo the
abstraction loss introduced by coarsening, so its contribution to the final cut
is bounded and is not isolated here.

*$k$-way search.* The pairwise organization measured in Table VII scales poorly
with $k$ and, unlike the direct $k$-way refinement used by KaHyPar
[@schlag2023], it can be trapped in local minima of individual pairs.

*Parallelism.* Coarsening, refinement and uncoarsening are single-threaded; only
the multi-start loop is parallel. Shared-memory partitioners such as Mt-KaHyPar
parallelize the core search [@gottesburen2024], which ckpttn does not.

*Interpreted reference.* The Python numbers are dominated by the interpreter
rather than by the algorithm and should be read only as a cross-language
consistency check.

## Concluding Remarks {#sec:conclusion}

ckpttn shows that a classical partitioner can be both simple and trustworthy.
Keeping FM but making the gain bookkeeping cheap, contracting aggressively with
a primal-dual matching and duplicate-net pruning, and certifying the coarsest
level by exact enumeration yields a multilevel partitioner whose three ports
agree and whose behaviour we can account for end to end. We do not establish
parity with dedicated state-of-the-art partitioners, and its remaining
scalability limits are stated in Section V-H. That agreement is not
an accident of coding: because the pass skeleton and the gain, constraint, and
partition policies are separated, the ports differ only in data layout, and the
same separation is what made the inner-loop engineering -- the no-op gain
updates, the reusable buffers, the borrowed neighbours -- safe to apply
uniformly. The experiments
confirm the expected trade-offs -- multilevel refinement buys 27-54 percent of
cut at roughly three times the runtime, and a greedy refiner trades 1.4-2.2
times the cut for 8-35 times the speed -- and the explicit
balance warning removes the silent-failure mode that complicates automated
tuning and reproducibility.

Natural next steps are a flat (single-array) graph layout in the Rust port to
close the remaining gap to C++, a parallel FM refinement [@gottesburen2024], a
timing-aware refinement in the spirit of TritonPart [@bustany2023], and a
systematic study of the contraction guard and leaf threshold across the IBM
benchmark family [@catalyurek2023].

## References {-}