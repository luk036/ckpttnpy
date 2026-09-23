#! /usr/bin/env python3
"""Shared scaffolding for the example partitioning scripts.

``Experiment`` is a Template Method: it fixes the argv -> parse -> load ->
multi-start -> report skeleton and lets each script fill in its description,
arguments, input and balance tolerance. ``plot_partition`` is the plotting
strategy shared by the scripts.
"""

import argparse
import logging
import random
import sys
from typing import Any, List, Tuple

import matplotlib.pyplot as plt
import networkx as nx
from netlistx.netlist import Netlist

from ckpttnpy import __version__
from ckpttnpy.harness import make_init_part, multi_start
from ckpttnpy.partitioner import create_partitioner

N_STARTS = 10

_logger = logging.getLogger(__name__)


def setup_logging(loglevel: Any) -> None:
    """Configure the root logger for the example scripts."""
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=loglevel,
        stream=sys.stdout,
        format=logformat,
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def add_common_arguments(parser: argparse.ArgumentParser) -> None:
    """Add the options every experiment shares."""
    parser.add_argument(
        "--version", action="version", version=f"ckpttnpy {__version__}"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        dest="loglevel",
        help="set loglevel to INFO",
        action="store_const",
        const=logging.INFO,
    )
    parser.add_argument(
        "-vv",
        "--very-verbose",
        dest="loglevel",
        help="set loglevel to DEBUG",
        action="store_const",
        const=logging.DEBUG,
    )
    parser.add_argument(
        "-p",
        "--plot",
        dest="plot",
        help="plot the result graphically",
        action="store_const",
        const=True,
    )


def run_multistart(
    hyprgraph: Netlist, k: int, bal_tol: float, rng: random.Random
) -> Tuple[int, Any]:
    """Run the FM partitioner from ``N_STARTS`` random starts, keep the best."""
    part_mgr = create_partitioner(k, "FM", bal_tol)

    def one() -> Tuple[int, Any]:
        part = make_init_part(hyprgraph, k, rng)
        part_mgr.run_Partition(hyprgraph, hyprgraph.module_weight, part)
        return part_mgr.totalcost, part

    return multi_start(N_STARTS, one)


def plot_partition(
    hyprgraph: Netlist, part: Any, k: int, colors: Tuple[str, ...] = ("g", "r", "b")
) -> None:
    """Draw the partition with one colour per part."""
    pos = nx.spring_layout(hyprgraph.ugraph)
    for kk in range(k):
        nodes = [i for i in hyprgraph if part[i] == kk]
        nx.draw_networkx_nodes(
            hyprgraph.ugraph,
            nodelist=nodes,
            node_color=colors[kk],
            node_size=50,
            pos=pos,
        )
    nx.draw_networkx_nodes(
        hyprgraph.ugraph,
        nodelist=hyprgraph.nets,
        node_color="k",
        node_size=20,
        pos=pos,
    )
    nx.draw_networkx_edges(hyprgraph.ugraph, pos=pos, width=1)
    plt.show()


class Experiment:
    """Template Method base for the example scripts."""

    description = ""
    k = 2

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """Register the script-specific positional/optional arguments."""
        raise NotImplementedError

    def check_args(self, args: argparse.Namespace) -> bool:
        """Validate *args*; return ``False`` to abort."""
        return True

    def load(self, args: argparse.Namespace) -> Netlist:
        """Build the netlist to partition."""
        raise NotImplementedError

    def get_bal_tol(self, args: argparse.Namespace) -> float:
        """Return the balance tolerance for this run."""
        return args.bal_tol

    def main(self, argv: List[str]) -> None:
        """Run the experiment."""
        parser = argparse.ArgumentParser(description=self.description)
        add_common_arguments(parser)
        self.add_arguments(parser)
        args = parser.parse_args(argv)
        setup_logging(args.loglevel)

        if not self.check_args(args):
            return

        hyprgraph = self.load(args)
        cost, part = run_multistart(
            hyprgraph, self.k, self.get_bal_tol(args), random.Random()
        )
        print(f"total cost = {cost}")

        if args.plot:
            plot_partition(hyprgraph, part, self.k)
        _logger.info("Script ends here")
