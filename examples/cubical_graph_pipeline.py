"""Step-by-step topological analysis for a cubical graph."""

from __future__ import annotations

from pathlib import Path

from topographer import (
    check_graph,
    compute_contour_tree_from_trees,
    compute_join_tree,
    compute_persistence,
    compute_split_tree,
    ensure_total_order,
    make_cubical_graph,
    save_graph_plot,
    save_tree_plot,
    simplify_tree_by_persistence,
)

SCALAR = "scalar"
SIMPLIFY_THRESHOLD = 0.5
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "output" / "cubical_graph_pipeline"


def main(output_dir: Path = OUTPUT_DIR) -> None:
    """Run the cubical-graph walkthrough."""

    graph = make_cubical_graph(scalar=SCALAR)

    print("Input graph node scalars:")
    print({node: graph.nodes[node][SCALAR] for node in graph.nodes})

    validated_scalars = check_graph(graph, SCALAR)
    print("\nValidated scalars:")
    print(validated_scalars)

    ordered_graph, ordered_scalars = ensure_total_order(graph, SCALAR)
    print("\nOrdered scalars:")
    print(ordered_scalars)

    join_tree = compute_join_tree(ordered_graph, SCALAR)
    print("\nJoin tree edges:")
    print(sorted(tuple(sorted(edge)) for edge in join_tree.graph.edges()))

    split_tree = compute_split_tree(ordered_graph, SCALAR)
    print("\nSplit tree edges:")
    print(sorted(tuple(sorted(edge)) for edge in split_tree.graph.edges()))

    contour_tree = compute_contour_tree_from_trees(split_tree, join_tree)
    print("\nContour tree edges:")
    print(sorted(tuple(sorted(edge)) for edge in contour_tree.graph.edges()))

    output_dir.mkdir(parents=True, exist_ok=True)
    original_graph_path = save_graph_plot(
        graph,
        output_dir / "01_original_graph.svg",
        scalar=SCALAR,
        title="Original Graph",
    )
    split_tree_path = save_tree_plot(
        split_tree,
        output_dir / "02_split_tree.svg",
        title="Split Tree",
    )
    join_tree_path = save_tree_plot(
        join_tree,
        output_dir / "03_join_tree.svg",
        title="Join Tree",
    )
    contour_tree_path = save_tree_plot(
        contour_tree,
        output_dir / "04_contour_tree.svg",
        title="Contour Tree",
    )
    print("\nWrote SVG plots:")
    print([original_graph_path.name, split_tree_path.name, join_tree_path.name, contour_tree_path.name])

    persistence_pairs = compute_persistence(contour_tree, scalar=SCALAR)
    print("\nPersistence pairs:")
    print(
        [
            (pair.extremum, pair.saddle, pair.persistence, pair.kind)
            for pair in persistence_pairs
        ]
    )

    simplified_contour_tree = simplify_tree_by_persistence(
        contour_tree,
        persistence_pairs,
        threshold=SIMPLIFY_THRESHOLD,
    )
    print(f"\nSimplified contour tree edges (threshold={SIMPLIFY_THRESHOLD}):")
    print(sorted(tuple(sorted(edge)) for edge in simplified_contour_tree.graph.edges()))


if __name__ == "__main__":
    main()
