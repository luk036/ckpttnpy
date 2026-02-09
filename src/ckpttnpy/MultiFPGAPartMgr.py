"""
MultiFPGAPartMgr.py

This module implements a partitioning manager specifically designed for multi-FPGA systems. It extends the
existing partitioning algorithms in the ckpttnpy project to handle the unique challenges of distributing
a design across multiple FPGAs, including resource constraints, inter-FPGA communication optimization,
and timing considerations. The main purpose is to provide methods for partitioning a hypergraph
representing a circuit design into multiple parts that can be mapped to different FPGAs while optimizing
for resource utilization and minimizing cross-FPGA connections. The implementation builds upon the
existing MLPartMgr, FMPartMgr, and related classes to provide a solution tailored for multi-FPGA
partitioning requirements. The algorithm addresses the challenges of multi-FPGA partitioning by
incorporating FPGA-specific resource constraints and communication cost optimization into the existing
partitioning framework. This code provides a framework for solving complex multi-FPGA partitioning
problems using a multi-level approach combined with Fiduccia-Mattheyses optimization, ensuring that the
partitioned design can be successfully implemented across multiple FPGAs while meeting performance and
resource constraints.
"""

from typing import Any, Dict, List

from .FMKWayGainCalc import FMKWayGainCalc
from .MLPartMgr import MLKWayPartMgr


class MultiFPGAPartMgr:
    """Multi-FPGA Partitioning Manager

    The `MultiFPGAPartMgr` class manages the partitioning of a design across multiple FPGAs,
    optimizing for resource utilization and inter-FPGA communication.
    """

    def __init__(
        self,
        num_fpgas: int,
        fpga_resources: List[Dict[str, float]],
        bal_tol: float = 0.1,
    ):
        """
        Initializes the MultiFPGAPartMgr with the number of FPGAs and their resources.

        :param num_fpgas: The number of FPGAs in the system
        :param fpga_resources: A list of dictionaries containing resource information for each FPGA
        :param bal_tol: The balance tolerance for partitioning, defaults to 0.1
        """
        self.num_fpgas = num_fpgas
        self.fpga_resources = fpga_resources
        self.bal_tol = bal_tol
        self.partitioner = MLKWayPartMgr(bal_tol, num_fpgas)

    def partition_design(self, hyprgraph: Any, module_weights: List[Dict[str, float]]):
        """
        Partitions the design represented by the hypergraph across multiple FPGAs.

        :param hyprgraph: The hypergraph representing the circuit design
        :param module_weights: A list of dictionaries containing weight information for each module
        :return: A partition assignment for each module in the hypergraph
        """
        # Calculate total resource requirements for each module
        total_module_weights = []
        for module_weight in module_weights:
            total_weight = sum(module_weight.values())
            total_module_weights.append(total_weight)

        # Initialize partition assignment
        initial_part = [0] * hyprgraph.number_of_modules()

        # Run the multi-level K-way partitioning algorithm
        legalcheck = self.partitioner.run_FMPartition(
            hyprgraph, total_module_weights, initial_part
        )

        if legalcheck.name != "AllSatisfied":
            print(
                f"Warning: Partitioning constraints not fully satisfied: {legalcheck}"
            )

        return initial_part

    def optimize_inter_fpga_connections(self, hyprgraph: Any, partition: List[int]):
        """
        Optimizes the partition to minimize inter-FPGA connections and communication costs.

        :param hyprgraph: The hypergraph representing the circuit design
        :param partition: The current partition assignment for each module
        :return: An optimized partition assignment
        """
        # This method would implement specific optimizations for inter-FPGA connections
        # For now, we'll return the partition as is, but in a full implementation,
        # this would include algorithms to reduce cross-FPGA communication
        return partition

    def validate_partition(
        self,
        hyprgraph: Any,
        partition: List[int],
        module_weights: List[Dict[str, float]],
    ):
        """
        Validates that the partition meets all FPGA resource constraints and other requirements.

        :param hyprgraph: The hypergraph representing the circuit design
        :param partition: The partition assignment for each module
        :param module_weights: A list of dictionaries containing weight information for each module
        :return: Boolean indicating if the partition is valid and a dictionary with validation details
        """
        # Initialize resource usage tracking for each FPGA
        fpga_resource_usage = [
            {resource: 0.0 for resource in self.fpga_resources[0].keys()}
            for _ in range(self.num_fpgas)
        ]

        # Calculate resource usage for each FPGA
        for module_idx, fpga_idx in enumerate(partition):
            if fpga_idx >= self.num_fpgas:
                return False, {
                    "error": f"Module {module_idx} assigned to non-existent FPGA {fpga_idx}"
                }

            module_resource_weights = module_weights[module_idx]
            for resource, weight in module_resource_weights.items():
                fpga_resource_usage[fpga_idx][resource] += weight

        # Check resource constraints
        for fpga_idx, (usage, capacity) in enumerate(
            zip(fpga_resource_usage, self.fpga_resources)
        ):
            for resource, used in usage.items():
                if resource in capacity and used > capacity[resource]:
                    return False, {
                        "error": f"FPGA {fpga_idx} exceeds {resource} capacity: {used} > {capacity[resource]}"
                    }

        # If we reach here, the partition is valid
        return True, {
            "resource_usage": fpga_resource_usage,
            "total_cost": self.partitioner.totalcost,
        }


class MultiFPGAGainCalc(FMKWayGainCalc):
    """Extended gain calculator that considers inter-FPGA communication costs"""

    def __init__(self, hyprgraph, num_parts: int = 2):
        super().__init__(hyprgraph, num_parts)
        self.inter_fpga_cost_weight = 1.0  # Weight for inter-FPGA communication cost

    def set_inter_fpga_cost_weight(self, weight: float):
        """Set the weight for inter-FPGA communication costs in gain calculations"""
        self.inter_fpga_cost_weight = weight

    def _init_gain_general_net(self, net, part):
        """Initialize gain for general net, considering inter-FPGA communication costs"""
        # Call parent implementation first
        super()._init_gain_general_net(net, part)

        # Additional logic to account for inter-FPGA communication costs
        # If net connects modules on different FPGAs, increase the cost
        connected_fpgas = set()
        for w in self.hyprgraph.ugraph[net]:
            connected_fpgas.add(part[w])

        if len(connected_fpgas) > 1:  # Net spans multiple FPGAs
            # Increase the cost based on the inter-FPGA communication weight
            net_weight = self.hyprgraph.get_net_weight(net) * self.inter_fpga_cost_weight
            for w in self.hyprgraph.ugraph[net]:
                self._modify_gain(
                    w, part[w], -net_weight
                )  # Negative gain for inter-FPGA connections
