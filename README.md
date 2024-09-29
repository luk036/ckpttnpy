# 🔪 ckpttnpy

> Circuit Partitioning Python Code

[![Documentation Status](https://readthedocs.org/projects/ckpttnpy/badge/?version=latest)](https://ckpttnpy.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/luk036/ckpttnpy/branch/master/graph/badge.svg)](https://codecov.io/gh/luk036/ckpttnpy)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/1c8b47586d12409e95c7c143b1fec7e8)](https://app.codacy.com/app/luk036/ckpttnpy?utm_source=github.com&utm_medium=referral&utm_content=luk036/ckpttnpy&utm_campaign=Badge_Grade_Dashboard)
[![CodeFactor](https://www.codefactor.io/repository/github/luk036/ckpttnpy/badge)](https://www.codefactor.io/repository/github/luk036/ckpttnpy)
[![Maintainability](https://api.codeclimate.com/v1/badges/2551a7289b83520b6cac/maintainability)](https://codeclimate.com/github/luk036/ckpttnpy/maintainability)

This code defines a system for managing multi-level partitioning, which is a technique used to divide a large problem into smaller, more manageable parts. The main purpose of this code is to provide a framework for partitioning a hypergraph (a type of graph where edges can connect more than two vertices) into multiple parts while maintaining certain balance and optimization criteria.

## The Main Algorithm

The main algorithm used in this system is a multi-level partitioning algorithm. This algorithm starts with an initial partitioning of the modules and then iteratively refines the partitioning by moving modules between parts to improve the balance and optimization criteria. The algorithm continues until it reaches a stable solution or a predefined stopping criterion is met.

The main input for this system is a hypergraph, module weights (which represent the importance or size of each module in the graph), and an initial partitioning of the modules. The output is an optimized partitioning of the modules that satisfies certain balance constraints and minimizes the total cost of the partitioning.

The core of the algorithm is in the run_FMPartition method of the MLPartMgr class. This method takes the hypergraph, module weights, and initial partitioning as input. It first checks if the initial partitioning is legal (satisfies the balance constraints). If it's not legal, it returns without making changes. If it is legal, it proceeds to optimize the partitioning.

The optimization process involves two main steps:

1. If the hypergraph is large enough (determined by the limitsize property), it first contracts the hypergraph into a smaller one. This is a way of simplifying the problem. It then recursively calls itself on this smaller hypergraph.

2. After the recursive call (or if the hypergraph was small enough to begin with), it calls an optimize function that attempts to improve the partitioning.

## Clustering Algorithm

A clustering algorithm for graph contraction is used. The main purpose is to simplify a complex graph (called a hypergraph) by grouping together certain nodes (called modules) into clusters. This process helps in reducing the complexity of the graph while maintaining its essential structure.

The code takes as input a hypergraph (represented by the Netlist class), weights for modules and clusters, and a set of forbidden nets (connections that should not be grouped). It produces as output a new, simplified graph (called a hierarchical netlist) with updated weights for the modules.

The algorithm works through several steps to achieve its purpose:

1. It starts by finding a minimum maximal matching in the graph, which is a way of pairing up nodes that are connected.

2. Then, it sets up the initial clusters, nets, and cell list based on this matching.

3. Next, it constructs a new graph based on these clusters and remaining nodes.

4. The code then purges duplicate nets, which are connections that essentially represent the same thing. This step helps further simplify the graph.

5. After purging duplicates, it reconstructs the graph with the updated information.

6. Finally, it contracts the subgraph, which means it combines the clustered nodes into single units in the new graph.

Throughout this process, the code keeps track of weights for modules and nets, updating them as nodes are combined into clusters. This is important because the weights represent the importance or size of each module or connection in the graph.

The main logic flow involves transforming the original complex graph into a simpler one by grouping connected nodes, removing redundant connections, and updating the weights accordingly. This is achieved through a series of graph operations and data structure manipulations.

For a beginner programmer, it's important to understand that this code is dealing with graph theory concepts, which are used to represent complex relationships between objects. The algorithm is trying to simplify these relationships while preserving the most important information. This kind of algorithm is useful in many fields, including circuit design, network analysis, and data compression.

## Other Details

The algorithm uses several helper classes (GainCalc, GainMgr, ConstrMgr, PartMgr) to manage different aspects of the partitioning process. These classes handle things like calculating the gain of moving a module from one partition to another, managing the constraints of the partitioning, and performing the actual optimization.

An important concept in this code is the idea of 'gain'. The gain represents how much the overall cost of the partitioning would improve if a particular change was made. The algorithm tries to make changes that have positive gain, improving the overall quality of the partitioning.

The code also includes a mechanism for taking 'snapshots' of the partitioning when a move results in a negative gain. This allows the algorithm to potentially backtrack if a series of moves ends up being unfavorable overall.

In summary, this code provides a flexible framework for solving complex partitioning problems, with the ability to handle different types of partitioning (binary or k-way) and to work on problems of different sizes through its multi-level approach.

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
