"""Step-by-step topological analysis for a small path graph."""

from __future__ import annotations

from topographer import (
    check_graph,
    compute_contour_tree_from_trees,
    compute_join_tree,
    compute_persistence,
    compute_split_tree,
    ensure_total_order,
    make_path_graph,
    simplify_tree_by_persistence,
)

SCALAR = "scalar"
SIMPLIFY_THRESHOLD = 0.5


def main() -> None:
    """Run the path-graph walkthrough."""

    graph = make_path_graph(scalar=SCALAR)

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
