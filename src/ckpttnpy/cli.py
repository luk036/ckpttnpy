"""CLI for hypergraph partitioning compatible with hMetis and KaHyPar."""

import argparse
import json
import random
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Optional, Set, Tuple

import networkx as nx
from netlistx.readwrite import read_are, read_netd


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
    """Read hypergraph from JSON format."""
    with open(filename, "r") as f:
        data = json.load(f)

    num_vertices = 0
    module_weights: List[int] = [1]
    nets: List[List[int]] = []

    if "nets" in data:
        nets = data["nets"]
        module_weights = data.get("weights", [1] * len(nets[0]) if nets else [])
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
    elif isinstance(data, list):
        nets = data
        num_vertices = max(max(n) for n in nets) + 1 if nets else 0
    else:
        raise ValueError(f"Unknown JSON format in {filename}")

    if not num_vertices:
        num_vertices = max((max(net) for net in nets if net), default=0) + 1

    graph = nx.Graph()
    graph.add_nodes_from(range(num_vertices), bipartite=0)
    graph.add_nodes_from(range(num_vertices, num_vertices + len(nets)), bipartite=1)

    for net_idx, net in enumerate(nets):
        global_net_idx = num_vertices + net_idx
        for vidx in net:
            if 0 <= vidx < num_vertices:
                graph.add_edge(global_net_idx, vidx)

    if len(module_weights) < num_vertices:
        module_weights.extend([1] * (num_vertices - len(module_weights)))

    return graph, module_weights[:num_vertices]


def read_yosys_json(filename: str) -> Tuple[nx.Graph, List[int], Set[int]]:
    """Read a Yosys synthesis JSON file and return hypergraph + fixed module set.

    Maps cells → module nodes (weight 1), ports → pad nodes (weight 0, fixed),
    and integer net IDs → net nodes.
    """
    with open(filename, "r") as f:
        data = json.load(f)

    modules = data["modules"]
    top_name = next(iter(modules))
    top = modules[top_name]

    cell_names: List[str] = list(top.get("cells", {}).keys())
    num_cells = len(cell_names)

    ports = top.get("ports", {})
    port_names = list(ports.keys())
    num_ports = len(port_names)

    all_nets: Set[int] = set()
    for port_info in ports.values():
        for bit in port_info.get("bits", []):
            if isinstance(bit, int):
                all_nets.add(bit)
    for netinfo in top.get("netnames", {}).values():
        for bit in netinfo.get("bits", []):
            if isinstance(bit, int):
                all_nets.add(bit)
    for cell_info in top.get("cells", {}).values():
        for conns in cell_info.get("connections", {}).values():
            for net_id in conns:
                if isinstance(net_id, int):
                    all_nets.add(net_id)

    nets_list = sorted(all_nets)
    num_nets = len(nets_list)
    net_start = num_cells + num_ports
    net_to_node = {net: net_start + i for i, net in enumerate(nets_list)}

    total_nodes = net_start + num_nets
    graph = nx.Graph()
    graph.add_nodes_from(range(num_cells + num_ports), bipartite=0)
    graph.add_nodes_from(range(net_start, total_nodes), bipartite=1)

    for i, name in enumerate(cell_names):
        for conns in top["cells"][name].get("connections", {}).values():
            for net_id in conns:
                if isinstance(net_id, int) and net_id in net_to_node:
                    graph.add_edge(i, net_to_node[net_id])

    port_start = num_cells
    for pi, name in enumerate(port_names):
        for bit in ports[name].get("bits", []):
            if isinstance(bit, int) and bit in net_to_node:
                graph.add_edge(port_start + pi, net_to_node[bit])

    module_weights: List[int] = [1] * num_cells + [0] * num_ports
    module_fixed: Set[int] = set(range(port_start, port_start + num_ports))

    return graph, module_weights, module_fixed


def read_hypergraph_dimacs(filename: str) -> Tuple[nx.Graph, List[int]]:
    """Read hypergraph from DIMACS format (.hgr)."""
    with open(filename, "r") as f:
        lines = f.readlines()

    num_vertices = 0
    nets: List[List[int]] = []

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
    filename: str,
    input_format: Optional[str] = None,
) -> Tuple[nx.Graph, List[int], Set[int]]:
    """Read hypergraph from file, auto-detecting format if not specified.

    Returns (graph, module_weights, module_fixed).
    """
    path = Path(filename)

    fmt = input_format.lower() if input_format else path.suffix.lower()
    module_fixed: Set[int] = set()
    graph: nx.Graph
    module_weights: List[int]

    if input_format == "yosys":
        graph, module_weights, module_fixed = read_yosys_json(filename)
    elif input_format == "ibm":
        graph, module_weights, module_fixed = read_hypergraph_ibm(filename)
    elif fmt in (".json", ".jsn"):
        graph, module_weights = read_hypergraph_json(filename)
    elif fmt in (".dimacs", ".hgr") and path.stem in ("hypergraph", "hgr"):
        graph, module_weights = read_hypergraph_dimacs(filename)
    else:
        graph, module_weights = read_hypergraph_hmetis(filename)

    return graph, module_weights, module_fixed


def read_hypergraph_ibm(
    filename: str,
) -> Tuple[nx.Graph, List[int], Set[int]]:
    """Read an IBM .net/.are pair and return (graph, module_weights, module_fixed).

    The companion .are file is located by replacing the .net suffix.
    """
    path = Path(filename)
    are_file = path.with_suffix(".are")

    hyprgraph = read_netd(filename)
    if are_file.exists():
        read_are(hyprgraph, str(are_file))

    graph = hyprgraph.ugraph
    module_weights = hyprgraph.module_weight
    module_fixed: Set[int] = (
        hyprgraph.module_fixed if isinstance(hyprgraph.module_fixed, set) else set()
    )
    return graph, module_weights, module_fixed


def read_fix_file(filename: str) -> Set[int]:
    """Read hMetis fix file: one module ID per line (0-based)."""
    fixed: Set[int] = set()
    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                fixed.add(int(line))
    return fixed


def write_partition(
    part: List[int],
    filename: Optional[str] = None,
    output_format: Optional[str] = None,
) -> None:
    """Write partition to file or stdout."""
    if output_format == "json":
        output = json.dumps(part, indent=2)
    else:
        output = "\n".join(str(p) for p in part)

    if filename:
        with open(filename, "w") as f:
            f.write(output)
    else:
        print(output)


def random_init_part(
    part: List[int],
    num_modules: int,
    num_parts: int,
    module_fixed: Set[int],
    rng: random.Random,
) -> None:
    """Randomize partition assignments for non-fixed modules."""
    for i in range(num_modules):
        if i not in module_fixed:
            part[i] = rng.randint(0, num_parts - 1)


PRESET_CHOICES = ["default", "quality", "highest_quality", "deterministic", "large_k"]
OBJECTIVE_CHOICES = ["cut", "km1", "soed", "km1a"]


def get_preset_config(preset: str) -> dict:
    """Return balance tolerance and recursive flag for a preset."""
    configs = {
        "default": {"bal_tol": 0.03, "recursive": True},
        "quality": {"bal_tol": 0.01, "recursive": False},
        "highest_quality": {"bal_tol": 0.005, "recursive": False},
        "deterministic": {"bal_tol": 0.03, "recursive": True},
        "large_k": {"bal_tol": 0.03, "recursive": True},
    }
    return configs.get(preset, configs["default"])


def run_one_partition(
    graph: nx.Graph,
    module_weights: List[int],
    module_fixed: Set[int],
    bal_tol: float,
    k: int,
    use_recursive: bool,
    rng: random.Random,
) -> Tuple[List[int], int]:
    """Run a single FM partitioning from a randomized start."""
    from netlistx.netlist import Netlist

    modules = [n for n in graph.nodes() if graph.nodes[n].get("bipartite") == 0]
    nets = [n for n in graph.nodes() if graph.nodes[n].get("bipartite") == 1]

    if not modules or not nets:
        return [0] * len(modules), 0

    netlist = Netlist(graph, modules, nets)
    init_part = [0] * len(modules)
    random_init_part(init_part, len(modules), k, module_fixed, rng)

    if k == 2:
        if use_recursive:
            from ckpttnpy.MLPartMgr import MLBiPartMgr

            part_mgr = MLBiPartMgr(bal_tol)
        else:
            from ckpttnpy.FMBiConstrMgr import FMBiConstrMgr
            from ckpttnpy.FMBiGainCalc import FMBiGainCalc
            from ckpttnpy.FMBiGainMgr import FMBiGainMgr
            from ckpttnpy.MLPartMgr import MLPartMgr
            from ckpttnpy.NNPartMgr import NNPartMgr

            part_mgr = MLPartMgr(
                FMBiGainCalc,
                FMBiGainMgr,
                FMBiConstrMgr,
                NNPartMgr,
                bal_tol,
                2,
            )
    else:
        if use_recursive:
            from ckpttnpy.MLPartMgr import MLKWayPartMgr

            part_mgr = MLKWayPartMgr(bal_tol, k)
        else:
            from ckpttnpy.FMKWayConstrMgr import FMKWayConstrMgr
            from ckpttnpy.FMKWayGainCalc import FMKWayGainCalc
            from ckpttnpy.FMKWayGainMgr import FMKWayGainMgr
            from ckpttnpy.MLPartMgr import MLPartMgr
            from ckpttnpy.NNPartMgr import NNPartMgr

            part_mgr = MLPartMgr(
                FMKWayGainCalc,
                FMKWayGainMgr,
                FMKWayConstrMgr,
                NNPartMgr,
                bal_tol,
                k,
            )

    part_mgr.run_Partition(netlist, module_weights, init_part)
    return init_part, part_mgr.totalcost


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
  %(prog)s circuit.hgr 2 5 -f fix.txt
  %(prog)s circuit.hgr 2 5 -s 42
  %(prog)s circuit.hgr 2 5 -t 8 -s 42
   %(prog)s circuit.json 2 5 -i yosys --verbose
   %(prog)s circuit.hgr 2 5 --mode direct --verbose
   %(prog)s ibm01.net 2 5 -i ibm --verbose
        """,
    )

    parser.add_argument("hypergraph_file", help="Input hypergraph file")
    parser.add_argument("k", type=int, nargs="?", help="Number of parts (default: 2)")
    parser.add_argument(
        "epsilon", type=float, nargs="?", help="Imbalance factor (default: 0.05)"
    )

    g_input = parser.add_argument_group("Input options")
    g_input.add_argument(
        "-i",
        "--input-format",
        choices=["hmetis", "json", "yosys", "dimacs", "ibm"],
        help="Input format (auto-detected from extension if not specified)",
    )
    g_input.add_argument(
        "-f",
        "--fixed",
        help="File with pre-assigned vertices (hMetis fix file: one ID per line)",
    )

    g_output = parser.add_argument_group("Output options")
    g_output.add_argument(
        "-o", "--output", help="Output partition file (default: stdout)"
    )
    g_output.add_argument(
        "--output-format",
        choices=["hmetis", "json"],
        default="hmetis",
        help="Output format (default: hmetis)",
    )
    g_output.add_argument(
        "-q", "--quiet", action="store_true", help="Suppress verbose output"
    )

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
        default="recursive",
        help="Mode: recursive=FMPartMgr, direct=NNPartMgr (default: recursive)",
    )
    g_algo.add_argument(
        "-t",
        "--threads",
        type=int,
        default=1,
        help="Number of starts for multi-start (default: 1)",
    )

    g_other = parser.add_argument_group("Other options")
    g_other.add_argument(
        "-s",
        "--seed",
        type=int,
        default=0,
        help="Random seed (0=random device, non-zero=deterministic)",
    )
    g_other.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    g_other.add_argument("--time-limit", type=int, help="Time limit in seconds")
    g_other.add_argument("--max-quality", type=int, help="Maximum quality (iterations)")

    args = parser.parse_args()

    k = args.k or 2
    epsilon_val = args.epsilon or 0.05
    quiet = args.quiet
    use_recursive = args.mode == "recursive"

    if k < 2:
        parser.error("k must be at least 2")
    if epsilon_val < 0:
        parser.error("epsilon must be non-negative")
    if epsilon_val > 1.0:
        epsilon_val /= 100.0

    if not quiet:
        print(f"Reading hypergraph from {args.hypergraph_file}...", file=sys.stderr)

    try:
        graph, module_weights, module_fixed = read_hypergraph(
            args.hypergraph_file, args.input_format
        )
    except FileNotFoundError:
        parser.error(f"File not found: {args.hypergraph_file}")
    except json.JSONDecodeError as e:
        parser.error(f"Invalid JSON format: {e}")
    except Exception as e:
        parser.error(f"Error reading hypergraph: {e}")

    if args.fixed:
        try:
            fix_ids = read_fix_file(args.fixed)
            module_fixed.update(fix_ids)
            if not quiet:
                print(
                    f"Fixed modules: {len(module_fixed)} "
                    f"({len(fix_ids)} from fix file)",
                    file=sys.stderr,
                )
        except FileNotFoundError:
            parser.error(f"Fix file not found: {args.fixed}")

    num_modules = len(
        [n for n in graph.nodes() if graph.nodes[n].get("bipartite") == 0]
    )
    num_nets = len([n for n in graph.nodes() if graph.nodes[n].get("bipartite") == 1])

    if not quiet:
        print(f"Hypergraph: {num_modules} vertices, {num_nets} nets", file=sys.stderr)
        print(f"K={k}, epsilon={epsilon_val}, preset={args.preset}", file=sys.stderr)

    num_starts = max(args.threads, 1)
    best_part: List[int] = [0] * num_modules
    best_cost = sys.maxsize

    if num_starts == 1:
        rng = random.Random(args.seed if args.seed != 0 else None)
        best_part, best_cost = run_one_partition(
            graph,
            module_weights,
            module_fixed,
            epsilon_val,
            k,
            use_recursive,
            rng,
        )
        if not quiet:
            print(f"Partitioning cost: {best_cost}", file=sys.stderr)
    else:
        if not quiet:
            base_msg = f"Base seed: {args.seed}" if args.seed != 0 else "Random seeds"
            print(f"{base_msg}, starts: {num_starts}", file=sys.stderr)
            print(
                f"Running partitioning (preset: {args.preset}, "
                f"mode: {args.mode})...",
                file=sys.stderr,
            )

        with ThreadPoolExecutor(max_workers=num_starts) as executor:
            futures = {}
            for start in range(num_starts):
                start_seed = args.seed + start * 104729 if args.seed != 0 else None
                rng = random.Random(start_seed)
                fut = executor.submit(
                    run_one_partition,
                    graph,
                    module_weights,
                    module_fixed,
                    epsilon_val,
                    k,
                    use_recursive,
                    rng,
                )
                futures[fut] = start + 1

            for fut in as_completed(futures):
                start_num = futures[fut]
                local_part, local_cost = fut.result()
                if not quiet:
                    print(
                        f"  Start {start_num}/{num_starts} cost: {local_cost}",
                        file=sys.stderr,
                    )
                if local_cost < best_cost:
                    best_cost = local_cost
                    best_part = local_part

        if not quiet:
            print(f"Partitioning cost: {best_cost}", file=sys.stderr)

    modules = [n for n in graph.nodes() if graph.nodes[n].get("bipartite") == 0]
    if k == 2:
        from ckpttnpy.FMBiConstrMgr import FMBiConstrMgr

        constr_mgr = FMBiConstrMgr(modules, epsilon_val, module_weights, k)
    else:
        from ckpttnpy.FMKWayConstrMgr import FMKWayConstrMgr

        constr_mgr = FMKWayConstrMgr(modules, epsilon_val, module_weights, k)
    if not constr_mgr.final_check(best_part):
        print(
            "Warning: final partition does not satisfy the balance constraint",
            file=sys.stderr,
        )

    write_partition(best_part, args.output, args.output_format)

    if not quiet:
        print(f"Partition written to {args.output or 'stdout'}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(run_cli())
