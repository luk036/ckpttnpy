# 🔪 ckpttnpy

> Circuit Partitioning Python Code

[![Documentation Status](https://readthedocs.org/projects/ckpttnpy/badge/?version=latest)](https://ckpttnpy.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/luk036/ckpttnpy/branch/master/graph/badge.svg)](https://codecov.io/gh/luk036/ckpttnpy)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/1c8b47586d12409e95c7c143b1fec7e8)](https://app.codacy.com/app/luk036/ckpttnpy?utm_source=github.com&utm_medium=referral&utm_content=luk036/ckpttnpy&utm_campaign=Badge_Grade_Dashboard)
[![CodeFactor](https://www.codefactor.io/repository/github/luk036/ckpttnpy/badge)](https://www.codefactor.io/repository/github/luk036/ckpttnpy)
[![Maintainability](https://api.codeclimate.com/v1/badges/2551a7289b83520b6cac/maintainability)](https://codeclimate.com/github/luk036/ckpttnpy/maintainability)

This library defines a system for the management of multi-level partitioning, which is a technique used to divide a complex problem into smaller, more manageable parts. The primary objective of this library is to provide a framework for partitioning a hypergraph (a type of graph where edges can connect more than two vertices) into multiple parts while maintaining specific balance and optimization criteria.

The primary algorithmic approach utilized in this system is that of multi-level partitioning. The algorithm commences with an initial partitioning of the modules, subsequently undergoing iterative refinements through the transfer of modules between parts, with the objective of enhancing the balance and optimization criteria. The algorithm continues until a stable solution is reached or a predefined stopping criterion is met.

The primary inputs for this system are a hypergraph, module weights (which represent the relative importance or size of each module in the graph), and an initial partitioning of the modules. The output is an optimized partitioning of the modules that satisfies the specified balance constraints and minimizes the total cost of the partitioning.

The fundamental component of the algorithm is the run_FMPartition method, which is contained within the MLPartMgr class. This method accepts the hypergraph, module weights, and initial partitioning as inputs. The initial partitioning is first evaluated to ascertain its legality, that is, whether it satisfies the balance constraints. In the event that the initial partitioning is not found to be legal, the algorithm will return without implementing any changes. If the initial partitioning is found to be legal, the algorithm proceeds to optimize the partitioning.

The optimization process comprises two principal stages.

1. In the event that the hypergraph is sufficiently large (as determined by the limitsize property), the hypergraph is initially contracted into a smaller one. This represents a method of reducing the complexity of the problem. Subsequently, the process is invoked recursively on the aforementioned smaller hypergraph.

2. Subsequently, a recursive call is made (or alternatively, if the hypergraph is of a sufficiently small size, the process may commence directly). At this juncture, an optimize function is invoked with the objective of enhancing the partitioning.

## Clustering Algorithm

A clustering algorithm for graph contraction is employed. The primary objective is to reduce the complexity of a graph (referred to as a hypergraph) by consolidating specific nodes (termed modules) into clusters. This process serves to reduce the complexity of the graph while maintaining its essential structure.

The algorithm accepts as input a hypergraph (represented by the Netlist class), weights for modules and clusters, and a set of forbidden nets (connections that should not be grouped). The output is a new, simplified graph, referred to as a hierarchical netlist, with updated weights for the modules.

The algorithm operates through a series of steps to achieve its objective. Initially, it identifies a minimum maximal matching in the graph, which involves pairing nodes that are connected.

2. Subsequently, the initial clusters, nets, and cell list are established based on the aforementioned matching.

3. Subsequently, a new graph is constructed based on the aforementioned clusters and the remaining nodes.

4. Subsequently, the algorithm eliminates any duplicate nets, which are connections that essentially represent the same entity. This step serves to further simplify the graph.

5. Following the removal of duplicate data points, the graph is reconstructed with the updated information.

6. Ultimately, the subgraph is contracted, whereby the clustered nodes are merged into a single unit within the new graph.

Throughout the process, the algorithm maintains a record of the weights associated with modules and nets, updating them in accordance with the formation of clusters comprising nodes. This is a significant aspect of the process, as the assigned weights represent the relative importance or size of each module.

The primary logic flow entails transforming the original complex graph into a simplified one through the grouping of connected nodes, the removal of redundant connections, and the updating of weights in accordance with these changes. This is accomplished through a sequence of graph operations and data structure manipulations.

It is crucial for novice programmers to grasp that this algorithmic process is grounded in graph theory, which is employed to depict intricate connections between entities. The objective of the algorithm is to simplify these relationships while preserving the most important information. This kind of algorithm is useful in a number of fields, including circuit design, network analysis, and data compression.

## Additional Information

The algorithm employs a number of helper classes (GainCalc, GainMgr, ConstrMgr, PartMgr) to facilitate the management of disparate aspects of the partitioning process. These classes are responsible for calculating the gain of moving a module from one partition to another, managing the constraints of the partitioning process, and performing the actual optimization.

A significant concept within this algorithmic framework is that of "gain." The term "gain" is used to quantify the extent to which the overall cost of the partitioning would be reduced if a specific alteration were to be implemented. The algorithm attempts to implement changes that result in a positive gain, thereby enhancing the overall quality of the partitioning.

Furthermore, the library incorporates a mechanism for capturing "snapshots" of the partitioning process in instances where a relocation results in a negative gain. This enables the algorithm to potentially reverse a series of moves if they prove to be disadvantageous overall.

In conclusion, this library offers a versatile framework for addressing intricate partitioning challenges, encompassing the capacity to handle diverse partitioning types (binary or k-way) and to tackle problems of varying scales through its multi-level approach.

## Dependencies

- [luk036/mywheel](https://github.com/luk036/mywheel)
- [luk036/netlistx](https://github.com/luk036/netlistx)
- networkx/networkx

## 🛠️ Installation and Run

To setup develop environment:

    pip3 install git+https://github.com/luk036/mywheel.git
    pip3 install git+https://github.com/luk036/netlistx.git
    pip3 install -r ./requirements.txt &&
    python3 setup.py develop

To run unit tests:

    python3 setup.py test

## 👀 See also

- [ckpttn-cpp](https://github.com/luk036/ckpttn-cpp)

## 👉 Note

This project has been set up using PyScaffold 3.2.1. For details and usage
information on PyScaffold see <https://pyscaffold.org/>.
