from __future__ import annotations

import argparse
from collections import deque
from pathlib import Path
import sys
from time import perf_counter

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


def main() -> None:
    from topographer.algorithms.split_tree import compute_split_tree
    from topographer.io.load import load_graph
    from topographer.io.save import save_graph
    from topographer.plotting import draw_tree, save_figure
    from topographer.plotting.styles import CONTOUR_STYLE

    def _compute_trunk_layout(
        tree_graph, *, scalar_attr: str
    ) -> dict[object, tuple[float, float]]:
        root = max(tree_graph.nodes, key=lambda node: float(tree_graph.nodes[node][scalar_attr]))

        parent: dict[object, object | None] = {root: None}
        children: dict[object, list[object]] = {node: [] for node in tree_graph.nodes}
        depth: dict[object, int] = {root: 0}

        stack = [root]
        while stack:
            node = stack.pop()
            for neighbor in tree_graph.neighbors(node):
                if parent[node] is not None and neighbor == parent[node]:
                    continue
                if neighbor in parent:
                    continue
                parent[neighbor] = node
                depth[neighbor] = depth[node] + 1
                children[node].append(neighbor)
                stack.append(neighbor)

        leaves = [node for node in tree_graph.nodes if node != root and len(children[node]) == 0]
        trunk_leaf = max(leaves, key=lambda node: depth[node]) if leaves else root

        trunk_path: list[object] = []
        cursor: object | None = trunk_leaf
        while cursor is not None:
            trunk_path.append(cursor)
            cursor = parent[cursor]
        trunk_path.reverse()
        trunk_set = set(trunk_path)

        pos: dict[object, tuple[float, float]] = {
            node: (0.0, float(tree_graph.nodes[node][scalar_attr])) for node in trunk_path
        }

        for trunk_node in trunk_path:
            branch_roots = [child for child in children[trunk_node] if child not in trunk_set]
            for branch_index, branch_root in enumerate(branch_roots):
                sign = 1 if branch_index % 2 == 0 else -1

                queue: deque[tuple[object, int]] = deque([(branch_root, 1)])
                while queue:
                    node, dist_from_trunk = queue.popleft()
                    x_coord = sign * float(dist_from_trunk)
                    y_coord = float(tree_graph.nodes[node][scalar_attr])
                    pos[node] = (x_coord, y_coord)

                    for child in children[node]:
                        queue.append((child, dist_from_trunk + 1))

        return pos

    parser = argparse.ArgumentParser(
        description="Compute and plot split tree for an input graph file."
    )
    parser.add_argument(
        "input_graph", help="Path to input graph file (relative to project root or absolute)."
    )
    parser.add_argument("--scalar", default="fitness", help="Scalar node attribute name.")
    parser.add_argument(
        "--with-labels",
        dest="with_labels",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Show node labels on the split tree plot.",
    )
    args = parser.parse_args()

    def stage(step: int, total: int, message: str) -> None:
        print(f"[Stage {step}/{total}] {message}")

    total_stages = 6

    stage(1, total_stages, "Resolving input graph path")

    input_graph_path = Path(args.input_graph).expanduser()
    if not input_graph_path.is_absolute():
        input_graph_path = (PROJECT_ROOT / input_graph_path).resolve()

    if not input_graph_path.exists():
        raise FileNotFoundError(f"Input graph not found: {input_graph_path}")

    stage(2, total_stages, "Loading graph from disk")
    graph = load_graph(input_graph_path)

    stage(3, total_stages, "Computing split tree")
    split_start = perf_counter()
    split_tree = compute_split_tree(
        graph,
        scalar=args.scalar,
    )
    split_elapsed = perf_counter() - split_start
    print(f"[Stage 3/{total_stages}] Split tree finished in {split_elapsed:.2f}s")

    for node in split_tree.graph.nodes:
        metadata = split_tree.node_metadata.get(node, {})
        if args.scalar in metadata:
            split_tree.graph.nodes[node][args.scalar] = float(metadata[args.scalar])
            continue
        if node in graph.nodes and args.scalar in graph.nodes[node]:
            split_tree.graph.nodes[node][args.scalar] = float(graph.nodes[node][args.scalar])

    print("=== Topographer split-tree workflow ===")
    print(f"Input graph: {input_graph_path}")
    print(f"Raw graph nodes: {graph.number_of_nodes()}")
    print(f"Raw graph edges: {graph.number_of_edges()}")
    print(f"Split tree nodes: {split_tree.graph.number_of_nodes()}")
    print(f"Split tree edges: {split_tree.graph.number_of_edges()}")

    stage(4, total_stages, "Saving intermediate split tree")
    output_dir = PROJECT_ROOT / "examples" / "output" / "split_workflow"
    output_dir.mkdir(parents=True, exist_ok=True)
    trees_dir = output_dir / "trees"
    figures_dir = output_dir / "figures"
    trees_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    split_tree_path = trees_dir / "split_tree.pkl"
    split_tree_figure_path = figures_dir / "split_tree.svg"

    save_graph(split_tree.graph, split_tree_path)

    stage(5, total_stages, "Loading intermediate split tree")
    split_tree_graph = load_graph(split_tree_path)

    stage(6, total_stages, "Plotting and saving split tree figure")
    import matplotlib.pyplot as plt

    trunk_pos = _compute_trunk_layout(split_tree_graph, scalar_attr=args.scalar)
    figure, ax = plt.subplots(figsize=(10, 16), constrained_layout=True)

    plot_style = {
        **CONTOUR_STYLE,
        "minima": {**CONTOUR_STYLE["minima"], "node_size": 150, "alpha": 0.5},
        "maxima": {**CONTOUR_STYLE["maxima"], "node_size": 150, "alpha": 0.5},
        "saddles": {**CONTOUR_STYLE["saddles"], "alpha": 0.5},
        "regular": {**CONTOUR_STYLE["regular"], "alpha": 0.5},
        "edges": {**CONTOUR_STYLE["edges"], "alpha": 0.5},
    }

    figure, _ = draw_tree(
        split_tree_graph,
        pos=trunk_pos,
        ax=ax,
        scalar_attr=args.scalar,
        with_labels=args.with_labels,
        show_regular=False,
        show_scalar_axis=True,
        style=plot_style,
    )
    save_figure(figure, split_tree_figure_path)

    print("[Done] Workflow completed successfully")

    print("Saved outputs:")
    print(f"  - split_tree: {split_tree_path}")
    print(f"  - split_tree_plot: {split_tree_figure_path}")


if __name__ == "__main__":
    main()
