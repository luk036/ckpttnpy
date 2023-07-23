# type: ignore

# from ckpttnpy.min_cover import contract_subgraph
from ckpttnpy.FMPartMgr import FMPartMgr

# **Special code for two-pin nets**
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
    """The `MLPartMgr` class is a manager for machine learning parts, with functionality for calculating
    gains, managing gains, managing constraints, managing parts, and tracking total cost.
    """

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
        self._limitsize = 7  # magic number

    @property
    def limitsize(self):
        """
        The `limitsize` function is a property that returns the value of the `_limitsize` attribute.
        :return: The `limitsize` property is returning the value of the `_limitsize` attribute.
        """
        return self._limitsize

    @limitsize.setter
    def limitsize(self, limit):
        """
        The above function is a setter method that sets the value of the "_limitsize" attribute in a class.

        :param limit: The `limit` parameter is the value that will be assigned to the `_limitsize` attribute
        of the object
        """
        self._limitsize = limit

    def run_FMPartition(self, hgr, module_weight, part):
        """
        The `run_FMPartition` function performs a partitioning algorithm on a hypergraph, optimizing the
        partitioning based on module weights and balancing constraints.

        :param hgr: The "hgr" parameter represents a hypergraph, which is a mathematical structure used to
        model relationships between objects. It is not clear what specific properties or data the hypergraph
        in this code represents without further context
        :param module_weight: The `module_weight` parameter represents the weight of each module in the
        hypergraph. It is used in the optimization process to calculate the cost of each partition
        :param part: The `part` parameter is a list that represents the current partitioning of the modules
        in the hypergraph `hgr`. Each element in the list corresponds to a module and contains an integer
        value representing the partition number to which the module belongs
        :return: The function `run_FMPartition` returns the value of `legalcheck`.
        """

        def legalcheck_fn():
            """
            The function `legalcheck_fn` creates instances of various managers and uses them to perform a legal
            check on a given part, returning the result and the total cost.
            :return: two values: `legalcheck` and `part_mgr.totalcost`.
            """
            gain_mgr = self.GainMgr(self.GainCalc, hgr, self.num_parts)
            constr_mgr = self.ConstrMgr(
                hgr, self.bal_tol, module_weight, self.num_parts
            )
            part_mgr = self.PartMgr(hgr, gain_mgr, constr_mgr)
            legalcheck = part_mgr.legalize(part)
            return legalcheck, part_mgr.totalcost

        def optimize_fn():
            """
            The function `optimize_fn` optimizes a given part by calculating the total cost using various
            managers and returns the result.
            :return: the total cost calculated by the `part_mgr.optimize()` method.
            """
            gain_mgr = self.GainMgr(self.GainCalc, hgr, self.num_parts)
            constr_mgr = self.ConstrMgr(
                hgr, self.bal_tol, module_weight, self.num_parts
            )
            part_mgr = self.PartMgr(hgr, gain_mgr, constr_mgr)
            part_mgr.optimize(part)
            return part_mgr.totalcost

        legalcheck, totalcost = legalcheck_fn()
        if legalcheck != LegalCheck.AllSatisfied:
            self.totalcost = totalcost
            return legalcheck

        if hgr.number_of_modules() >= self._limitsize:  # OK
            hgr2, module_weight2 = contract_subgraph(hgr, module_weight, set())
            if hgr2.number_of_modules() <= hgr.number_of_modules():
                part2 = [0] * hgr2.number_of_modules()
                hgr2.projection_up(part, part2)
                legalcheck_recur = self.run_FMPartition(hgr2, module_weight2, part2)
                if legalcheck_recur == LegalCheck.AllSatisfied:
                    hgr2.projection_down(part2, part)

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
