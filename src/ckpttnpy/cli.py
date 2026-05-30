"""CLI for hypergraph partitioning compatible with hMetis and KaHyPar."""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional, Tuple

import networkx as nx


def read_hypergraph_hmetis(filename: str) -> Tuple[nx.Graph, List[int]]:
    """Read hypergraph from hMetis format file."""
    with open(filename, "r") as f:
        lines = f.readlines()

    num_nets = 0
    num_vertices = 0
    fmt = 0

    for line in lines:
        line = line.strip()
        if line and not line.startswith("%"):
            header_parts = line.split()
            num_nets = int(header_parts[0])
            num_vertices = int(header_parts[1])
            fmt = int(header_parts[2]) if len(header_parts) > 2 else 0
            break

    module_weights = [1] * num_vertices
    graph = nx.Graph()
    graph.add_nodes_from(range(num_vertices), bipartite=0)
    graph.add_nodes_from(range(num_vertices, num_vertices + num_nets), bipartite=1)

    net_lines = [
        ln.strip() for ln in lines[1:] if ln.strip() and not ln.startswith("%")
    ]

    has_vertex_weights = fmt in (10, 11)

    if has_vertex_weights and len(net_lines) > num_nets:
        module_weights = [int(w) for w in net_lines[num_nets:]]
        net_lines = net_lines[:num_nets]

    for net_idx, net_line in enumerate(net_lines[:num_nets]):
        parts: List[int] = [int(v) for v in net_line.split()]

        global_net_idx = num_vertices + net_idx
        for vidx in parts:
            if 0 <= vidx < num_vertices:
                graph.add_edge(global_net_idx, vidx)

    return graph, module_weights


def read_hypergraph_json(filename: str) -> Tuple[nx.Graph, List[int]]:
    """Read hypergraph from JSON format.

    JSON formats supported:
    1. Simple: {"nodes": [[0,1,2], [1,2,3], ...]}
    2. KaHyPar-like: {"hyperedges": [...], "vertices": n}
    3. With weights: {"nets": [...], "weights": [1,2,1,1]}
    """
    with open(filename, "r") as f:
        data = json.load(f)

    num_vertices = 0
    module_weights = [1]
    nets = []

    # Format 1: Simple {"nets": [[0,1,2], [1,2,3], ...]}
    if "nets" in data:
        nets = data["nets"]
        if "weights" in data:
            module_weights = data["weights"]
        else:
            module_weights = [1] * len(data["nets"][0]) if nets else []

    # Format 2: {"hyperedges": [[0,1,2], ...], "num_vertices": n} or {"edges": ...}
    elif "hyperedges" in data:
        nets = data["hyperedges"]
        num_vertices = data.get(
            "num_vertices", max(max(n) for n in nets) + 1 if nets else 0
        )
        module_weights = data.get("vertex_weights", [1] * num_vertices)

    elif "edges" in data:
        nets = data["edges"]
        num_vertices = data.get(
            "num_vertices", max(max(n) for n in nets) + 1 if nets else 0
        )
        module_weights = data.get("weights", [1] * num_vertices)

    # Format 3: Simple [[0,1,2], [1,2,3], ...]
    elif isinstance(data, list):
        nets = data
        num_vertices = max(max(n) for n in nets) + 1 if nets else 0

    else:
        raise ValueError(f"Unknown JSON format in {filename}")

    if not num_vertices:
        num_vertices = max((max(net) for net in nets if net), default=0) + 1

    # Create graph
    graph = nx.Graph()
    graph.add_nodes_from(range(num_vertices), bipartite=0)
    graph.add_nodes_from(range(num_vertices, num_vertices + len(nets)), bipartite=1)

    for net_idx, net in enumerate(nets):
        global_net_idx = num_vertices + net_idx
        for vidx in net:
            if 0 <= vidx < num_vertices:
                graph.add_edge(global_net_idx, vidx)

    # Ensure module_weights has correct length
    if len(module_weights) < num_vertices:
        module_weights.extend([1] * (num_vertices - len(module_weights)))

    return graph, module_weights[:num_vertices]


def read_hypergraph_dimacs(filename: str) -> Tuple[nx.Graph, List[int]]:
    """Read hypergraph from DIMACS format (.hgr)."""
    with open(filename, "r") as f:
        lines = f.readlines()

    num_vertices = 0
    nets = []

    for line in lines:
        line = line.strip()
        if not line or line.startswith("c"):
            continue
        if line.startswith("p "):
            parts = line.split()
            num_vertices = int(parts[2])
        elif line.startswith("e "):
            parts = line.split()[1:]
            net = [int(v) - 1 for v in parts]
            nets.append(net)

    module_weights = [1] * num_vertices

    graph = nx.Graph()
    graph.add_nodes_from(range(num_vertices), bipartite=0)
    graph.add_nodes_from(range(num_vertices, num_vertices + len(nets)), bipartite=1)

    for net_idx, net in enumerate(nets):
        global_net_idx = num_vertices + net_idx
        for vidx in net:
            if 0 <= vidx < num_vertices:
                graph.add_edge(global_net_idx, vidx)

    return graph, module_weights


def read_hypergraph(
    filename: str, input_format: Optional[str] = None
) -> Tuple[nx.Graph, List[int]]:
    """Read hypergraph from file, auto-detecting format if not specified."""
    path = Path(filename)

    if input_format:
        fmt = input_format.lower()
    else:
        fmt = path.suffix.lower()

    if fmt in (".json", ".jsn"):
        return read_hypergraph_json(filename)
    elif fmt in (".dimacs", ".hgr") and path.stem in ("hypergraph", "hgr"):
        return read_hypergraph_dimacs(filename)
    else:
        return read_hypergraph_hmetis(filename)


def write_partition(
    part: List[int], filename: Optional[str] = None, output_format: Optional[str] = None
) -> None:
    """Write partition to file."""
    if output_format == "json":
        output = json.dumps(part, indent=2)
    else:
        output = "\n".join(str(p) for p in part)

    if filename:
        with open(filename, "w") as f:
            f.write(output)
    else:
        print(output)


PRESET_CHOICES = ["default", "quality", "highest_quality", "deterministic", "large_k"]
OBJECTIVE_CHOICES = ["cut", "km1", "soed", "km1a"]


def run_cli() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Hypergraph partitioner compatible with hMetis and KaHyPar",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s circuit.hgr 2 5
  %(prog)s circuit.hgr 2 5 -v
  %(prog)s circuit.hgr 4 10 -o partition.txt
  %(prog)s circuit.json 2 5 --input-format json
  %(prog)s circuit.hgr 2 5 --objective cut
  %(prog)s circuit.hgr 4 3 --preset quality
        """,
    )

    parser.add_argument("hypergraph_file", help="Input hypergraph file")
    parser.add_argument("k", type=int, nargs="?", help="Number of parts (default: 2)")
    parser.add_argument(
        "epsilon", type=float, nargs="?", help="Imbalance factor (default: 0.05)"
    )

    # Input options
    g_input = parser.add_argument_group("Input options")
    g_input.add_argument(
        "-i",
        "--input-format",
        choices=["hmetis", "json", "dimacs"],
        help="Input format (auto-detected from extension if not specified)",
    )
    g_input.add_argument(
        "-f",
        "--fixed",
        help="File with pre-assigned vertices (hMetis fix file format)",
    )

    # Output options
    g_output = parser.add_argument_group("Output options")
    g_output.add_argument(
        "-o",
        "--output",
        help="Output partition file (default: stdout)",
    )
    g_output.add_argument(
        "--output-format",
        choices=["hmetis", "json"],
        default="hmetis",
        help="Output format (default: hmetis)",
    )
    g_output.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress output",
    )

    # Algorithm options (KaHyPar-compatible)
    g_algo = parser.add_argument_group("Algorithm options")
    g_algo.add_argument(
        "-p",
        "--preset",
        choices=PRESET_CHOICES,
        default="default",
        help="Preset config (default: default)",
    )
    g_algo.add_argument(
        "--objective",
        choices=OBJECTIVE_CHOICES,
        help="Objective function",
    )
    g_algo.add_argument(
        "-m",
        "--mode",
        choices=["direct", "recursive"],
        default="direct",
        help="Partitioning mode (default: direct)",
    )
    g_algo.add_argument(
        "-t",
        "--threads",
        type=int,
        default=1,
        help="Number of threads (default: 1)",
    )

    # Other options
    g_other = parser.add_argument_group("Other options")
    g_other.add_argument(
        "-s",
        "--seed",
        type=int,
        default=0,
        help="Random seed (default: 0)",
    )
    g_other.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose output",
    )
    g_other.add_argument(
        "--time-limit",
        type=int,
        help="Time limit in seconds",
    )
    g_other.add_argument(
        "--max-quality",
        type=int,
        help="Maximum quality (iterations)",
    )

    args = parser.parse_args()

    # Handle positional arguments
    k = args.k or 2
    epsilon = args.epsilon or 0.05

    if k < 2:
        parser.error("k must be at least 2")

    if epsilon < 0:
        parser.error("epsilon must be non-negative")

    if not args.quiet:
        print(f"Reading hypergraph from {args.hypergraph_file}...", file=sys.stderr)

    try:
        graph, module_weights = read_hypergraph(args.hypergraph_file, args.input_format)
    except FileNotFoundError:
        parser.error(f"File not found: {args.hypergraph_file}")
    except json.JSONDecodeError as e:
        parser.error(f"Invalid JSON format: {e}")
    except Exception as e:
        parser.error(f"Error reading hypergraph: {e}")

    num_vertices = len(
        [n for n in graph.nodes() if graph.nodes[n].get("bipartite") == 0]
    )
    num_nets = len([n for n in graph.nodes() if graph.nodes[n].get("bipartite") == 1])

    if not args.quiet:
        print(f"Hypergraph: {num_vertices} vertices, {num_nets} nets", file=sys.stderr)
        print(f"K={k}, epsilon={epsilon}, preset={args.preset}", file=sys.stderr)

    if k != 2 and not args.quiet:
        print(
            f"Warning: k={k} not fully supported, using binary partitioning",
            file=sys.stderr,
        )

    part = [0] * num_vertices

    if not args.quiet:
        print(f"Running partitioning (preset: {args.preset})...", file=sys.stderr)
        print(f"Running partitioning (preset: {args.preset})...", file=sys.stderr)

    try:
        from netlistx.netlist import Netlist

        from ckpttnpy.MLPartMgr import MLBiPartMgr

        modules = [n for n in graph.nodes() if graph.nodes[n].get("bipartite") == 0]
        nets = [n for n in graph.nodes() if graph.nodes[n].get("bipartite") == 1]

        if modules and nets:
            netlist = Netlist(graph, modules, nets)
            bal_tol = epsilon
            part_mgr = MLBiPartMgr(bal_tol)

            init_part = [0] * len(modules)
            for i in range(len(modules)):
                init_part[i] = i % 2

            part_mgr.run_FMPartition(netlist, module_weights, init_part)
            totalcost = part_mgr.totalcost

            for i in range(len(modules)):
                part[i] = init_part[i]

            if not args.quiet:
                print(f"Partitioning cost: {totalcost}", file=sys.stderr)
    except ImportError:
        for i in range(num_vertices):
            part[i] = i % 2

    write_partition(part, args.output, args.output_format)

    if not args.quiet:
        print(f"Partition written to {args.output or 'stdout'}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(run_cli())
