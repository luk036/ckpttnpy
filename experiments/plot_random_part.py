import argparse
import logging
import sys
from random import randint

import matplotlib.pyplot as plt
import networkx as nx
from netlistx.netlist import Netlist, create_random_hgraph

from ckpttnpy import __version__
from ckpttnpy.MLPartMgr import MLBiPartMgr

__author__ = "Wai-Shing Luk"
__copyright__ = "Wai-Shing Luk"
__license__ = "mit"

_logger = logging.getLogger(__name__)


def run_MLBiPartMgr(hyprgraph: Netlist):
    part_mgr = MLBiPartMgr(0.4)
    mincost = 100000000000
    minpart = []
    for _ in range(10):
        randseq = [randint(0, 1) for _ in hyprgraph]

        if isinstance(hyprgraph.modules, range):
            part = randseq
        elif isinstance(hyprgraph.modules, list):
            part = {v: k for v, k in zip(hyprgraph.modules, randseq)}
        else:
            raise NotImplementedError

        part_mgr.run_FMPartition(hyprgraph, hyprgraph.module_weight, part)
        if mincost > part_mgr.totalcost:
            mincost = part_mgr.totalcost
            minpart = part.copy()
    return mincost, minpart


def plot(hyprgraph: Netlist, part):
    part0 = [i for i in hyprgraph if part[i] == 0]
    part1 = [i for i in hyprgraph if part[i] == 1]
    pos = nx.spring_layout(hyprgraph.ugraph)
    nx.draw_networkx_nodes(
        hyprgraph.ugraph, nodelist=part0, node_color="g", node_size=50, pos=pos
    )
    nx.draw_networkx_nodes(
        hyprgraph.ugraph, nodelist=part1, node_color="r", node_size=50, pos=pos
    )
    nx.draw_networkx_nodes(
        hyprgraph.ugraph, nodelist=hyprgraph.nets, node_color="k", node_size=20, pos=pos
    )
    nx.draw_networkx_edges(hyprgraph.ugraph, pos=pos, width=1)
    plt.show()


def parse_args(args):
    """Parse command line parameters

    Args:
      args ([str]): command line parameters as list of strings

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = argparse.ArgumentParser(
        description="Multilevel Circuit Partition demonstration"
    )
    parser.add_argument(
        "--version", action="version", version="ckpttnpy {ver}".format(ver=__version__)
    )
    parser.add_argument(dest="N", help="number of modules", type=int, metavar="INT")
    parser.add_argument(dest="M", help="number of nets", type=int, metavar="INT")
    parser.add_argument(
        dest="eta", help="ratio of nets and pins", type=float, metavar="FLOAT"
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
    return parser.parse_args(args)


def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=loglevel,
        stream=sys.stdout,
        format=logformat,
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def main(args):
    """Main entry point allowing external calls

    Args:
      args ([str]): command line parameter list
    """
    args = parse_args(args)
    setup_logging(args.loglevel)
    _logger.debug("Starting crazy calculations...")
    # print("The {}-th Fibonacci number is {}".format(args.n, fib(args.n)))

    if args.eta >= 1:
        _logger.error("eta value {} is too big".format(args.eta))
        return
    if args.eta > 0.3:
        _logger.warning("eta value {} may be too big".format(args.eta))

    hyprgraph = create_random_hgraph(args.N, args.M, args.eta)
    totalcost, part = run_MLBiPartMgr(hyprgraph)
    print("total cost = {}".format(totalcost))

    if args.plot:
        plot(hyprgraph, part)
    _logger.info("Script ends here")


def run():
    """Entry point for console_scripts"""
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
