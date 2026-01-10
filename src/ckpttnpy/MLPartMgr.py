"""
MLPartMgr.py

This code defines a system for managing multi-level partitioning, which is a technique used to divide a large problem into smaller, more manageable parts. The main purpose of this code is to provide a framework for partitioning a hypergraph (a type of graph where edges can connect more than two vertices) into multiple parts while maintaining certain balance and optimization criteria.

The code defines three main classes: MLPartMgr, MLBiPartMgr, and MLKWayPartMgr. MLPartMgr is the base class, while the other two are specialized versions for different types of partitioning.

The main input for this system is a hypergraph, module weights (which represent the importance or size of each module in the graph), and an initial partitioning of the modules. The output is an optimized partitioning of the modules that satisfies certain balance constraints and minimizes the total cost of the partitioning.

The core of the algorithm is in the run_FMPartition method of the MLPartMgr class. This method takes the hypergraph, module weights, and initial partitioning as input. It first checks if the initial partitioning is legal (satisfies the balance constraints). If it's not legal, it returns without making changes. If it is legal, it proceeds to optimize the partitioning.

The optimization process involves two main steps:

1. If the hypergraph is large enough (determined by the limitsize property), it first contracts the hypergraph into a smaller one. This is a way of simplifying the problem. It then recursively calls itself on this smaller hypergraph.

2. After the recursive call (or if the hypergraph was small enough to begin with), it calls an optimize function that attempts to improve the partitioning.

The algorithm uses several helper classes (GainCalc, GainMgr, ConstrMgr, PartMgr) to manage different aspects of the partitioning process. These classes handle things like calculating the gain of moving a module from one partition to another, managing the constraints of the partitioning, and performing the actual optimization.

An important concept in this code is the idea of 'gain'. The gain represents how much the overall cost of the partitioning would improve if a particular change was made. The algorithm tries to make changes that have positive gain, improving the overall quality of the partitioning.

The code also includes a mechanism for taking 'snapshots' of the partitioning when a move results in a negative gain. This allows the algorithm to potentially backtrack if a series of moves ends up being unfavorable overall.

In summary, this code provides a flexible framework for solving complex partitioning problems, with the ability to handle different types of partitioning (binary or k-way) and to work on problems of different sizes through its multi-level approach.
"""

# type: ignore

import gc

# from ckpttnpy.min_cover import contract_subgraph
from ckpttnpy.FMPartMgr import FMPartMgr

from .FMBiConstrMgr import FMBiConstrMgr
from .FMBiGainCalc import FMBiGainCalc
from .FMBiGainMgr import FMBiGainMgr
from .FMConstrMgr import LegalCheck
from .FMKWayConstrMgr import FMKWayConstrMgr
from .FMKWayGainCalc import FMKWayGainCalc
from .FMKWayGainMgr import FMKWayGainMgr

# Take a snapshot when a move make **negative** gain.
# Snapshot in the form of "interface"???
from .min_cover import contract_subgraph


class MLPartMgr:
    """The `MLPartMgr` class is a manager for Multi-level Partitioning."""

    def __init__(
        self, GainCalc, GainMgr, ConstrMgr, PartMgr, bal_tol, num_parts=2
    ) -> None:
        """
        The function initializes an object with various attributes and assigns values to them.

        :param GainCalc: A class or function that calculates the gain. It is not specified what type it is,
            so it could be any type of object that performs gain calculations
        :param GainMgr: The `GainMgr` parameter is an object that manages the calculation and management of
            gains. It likely contains methods and attributes related to gain calculations and management
        :param ConstrMgr: A manager class that handles constraints for the optimization problem
        :param PartMgr: The `PartMgr` parameter is an object that manages the parts in the system. It likely
            has methods for adding, removing, and retrieving parts, as well as other operations related to
            managing parts
        :param bal_tol: The `bal_tol` parameter is a tolerance value used for balancing calculations. It is
            used to determine if the calculated gains are within an acceptable range of balance
        :param num_parts: The number of parts in the system. It is an optional parameter with a default
            value of 2, defaults to 2 (optional)
        """
        self.GainCalc = GainCalc
        self.GainMgr = GainMgr
        self.ConstrMgr = ConstrMgr
        self.PartMgr = PartMgr
        self.bal_tol = bal_tol
        self.num_parts = num_parts
        self.totalcost = 0
        self.LIMIT_SIZE = 7  # magic number

    @property
    def limitsize(self):
        """
        The `limitsize` function is a property that returns the value of the `_limitsize` attribute.
        :return: The `limitsize` property is returning the value of the `_limitsize` attribute.
        """
        return self.LIMIT_SIZE

    @limitsize.setter
    def limitsize(self, limit):
        """
        The above function is a setter method that sets the value of the "_limitsize" attribute in a class.

        :param limit: The `limit` parameter is the value that will be assigned to the `_limitsize` attribute
            of the object
        """
        self.LIMIT_SIZE = limit

    def run_FMPartition(self, hyprgraph, module_weight, part):
        """Run Fiduccia-Mattheyses Partitioning



        This function performs a partitioning algorithm on a hypergraph, optimizing the

        partitioning based on module weights and balancing constraints.



        :param hyprgraph: The "hyprgraph" parameter represents a hypergraph, which is a mathematical structure used to

            model relationships between objects. It is not clear what specific properties or data the hypergraph

            in this code represents without further context

        :param module_weight: The `module_weight` parameter represents the weight of each module in the

            hypergraph. It is used in the optimization process to calculate the cost of each partition

        :param part: The `part` parameter is a list that represents the current partitioning of the modules

            in the hypergraph `hyprgraph`. Each element in the list corresponds to a module and contains an integer

            value representing the partition number to which the module belongs

        :return: The function `run_FMPartition` returns the value of `legalcheck`.



        .. svgbob::



            "Multi-Level Partitioning Process"

          +------------------------------------------+

          |  Coarse Graph (Fewer Modules)            |

          |  [A, A, B, B, C, C]                     |

          |  (Recursive Call)                        |

          +------------------|-----------------------+

                             |

                             v

          +------------------V-----------------------+

          |  Fine Graph (More Modules)               |

          |  [A, A, A, B, B, B, C, C, C]           |

          |  (Detailed Optimization)                 |

          +------------------------------------------+

        """

        def legalcheck_fn():
            """
            The function `legalcheck_fn` creates instances of various managers and uses them to perform a legal
            check on a given part, returning the result and the total cost.

            :return: two values: `legalcheck` and `part_mgr.totalcost`.
            """
            gain_mgr = self.GainMgr(self.GainCalc, hyprgraph, self.num_parts)
            constr_mgr = self.ConstrMgr(
                hyprgraph, self.bal_tol, module_weight, self.num_parts
            )
            part_mgr = self.PartMgr(hyprgraph, gain_mgr, constr_mgr)
            legalcheck = part_mgr.legalize(part)
            return legalcheck, part_mgr.totalcost

        def optimize_fn():
            """
            The function `optimize_fn` optimizes a given part by calculating the total cost using various
            managers and returns the result.

            :return: the total cost calculated by the `part_mgr.optimize()` method.
            """
            gain_mgr = self.GainMgr(self.GainCalc, hyprgraph, self.num_parts)
            constr_mgr = self.ConstrMgr(
                hyprgraph, self.bal_tol, module_weight, self.num_parts
            )
            part_mgr = self.PartMgr(hyprgraph, gain_mgr, constr_mgr)
            part_mgr.optimize(part)
            return part_mgr.totalcost

        legalcheck, totalcost = legalcheck_fn()
        if legalcheck != LegalCheck.AllSatisfied:
            self.totalcost = totalcost
            return legalcheck

        if hyprgraph.number_of_modules() >= self.limitsize:  # OK
            try:
                hgr2, module_weight2 = contract_subgraph(
                    hyprgraph, module_weight, set()
                )
                # try: if 3 * hgr2.number_of_modules() <= 2 * hyprgraph.number_of_modules():
                part2 = [0] * hgr2.number_of_modules()
                hgr2.projection_up(part, part2)
                legalcheck_recur = self.run_FMPartition(hgr2, module_weight2, part2)
                if legalcheck_recur == LegalCheck.AllSatisfied:
                    hgr2.projection_down(part2, part)
            except MemoryError:
                print("MemoryError: Not enough memory available.")
                gc.collect()

        self.totalcost = optimize_fn()
        assert self.totalcost >= 0
        return legalcheck


# The MLBiPartMgr class is a subclass of MLPartMgr that initializes with specific parameters for
# balancing tolerance.
class MLBiPartMgr(MLPartMgr):
    def __init__(self, bal_tol):
        """
        The `__init__` function initializes an object with the given balance tolerance and calls the
        `__init__` function of the parent class `MLPartMgr` with specific arguments.

        :param bal_tol: The `bal_tol` parameter is the balance tolerance. It represents the maximum allowed
            imbalance between partitions in a multi-level partitioning algorithm. It is used to control the
            balance of the partitions, ensuring that they are as evenly distributed as possible
        """
        MLPartMgr.__init__(
            self, FMBiGainCalc, FMBiGainMgr, FMBiConstrMgr, FMPartMgr, bal_tol
        )


# The MLKWayPartMgr class is a subclass of MLPartMgr that initializes with specific parameters and
# inherits methods from various other classes.
class MLKWayPartMgr(MLPartMgr):
    def __init__(self, bal_tol, num_parts):
        """
        The function is a constructor that initializes an object with certain parameters and calls the
        constructor of a parent class.

        :param bal_tol: The `bal_tol` parameter represents the balance tolerance for the partitioning
            algorithm. It is a measure of how evenly the workload is distributed among the partitions. A lower
            value indicates a stricter balance requirement, while a higher value allows for more imbalance
        :param num_parts: The `num_parts` parameter represents the number of parts or partitions that will
            be created in the system
        """
        MLPartMgr.__init__(
            self,
            FMKWayGainCalc,
            FMKWayGainMgr,
            FMKWayConstrMgr,
            FMPartMgr,
            bal_tol,
            num_parts,
        )
