"""Shared runner for the example pipeline walkthrough scripts."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

import networkx as nx

from topographer import (
    check_graph,
    compute_contour_tree_from_trees,
    compute_join_tree,
    compute_persistence,
    compute_split_tree,
    ensure_total_order,
    save_graph_plot,
    save_persistence_diagram,
    save_tree_plot,
    simplify_tree_by_persistence,
)


def run_example_pipeline(
    *,
    build_graph: Callable[[str], nx.Graph],
    output_dir: Path,
    example_name: str,
    scalar: str = "scalar",
    simplify_threshold: float = 0.5,
) -> None:
    """Run the standard example pipeline for a graph builder."""

    graph = build_graph(scalar=scalar)

    print("Input graph node scalars:")
    print({node: graph.nodes[node][scalar] for node in graph.nodes})

    validated_scalars = check_graph(graph, scalar)
    print("\nValidated scalars:")
    print(validated_scalars)

    ordered_graph, ordered_scalars = ensure_total_order(graph, scalar)
    print("\nOrdered scalars:")
    print(ordered_scalars)

    join_tree = compute_join_tree(ordered_graph, scalar)
    print("\nJoin tree edges:")
    print(sorted(tuple(sorted(edge)) for edge in join_tree.graph.edges()))

    split_tree = compute_split_tree(ordered_graph, scalar)
    print("\nSplit tree edges:")
    print(sorted(tuple(sorted(edge)) for edge in split_tree.graph.edges()))

    contour_tree = compute_contour_tree_from_trees(split_tree, join_tree)
    print("\nContour tree edges:")
    print(sorted(tuple(sorted(edge)) for edge in contour_tree.graph.edges()))

    persistence_pairs = compute_persistence(contour_tree, scalar=scalar)
    print("\nContour tree persistence pairs:")
    print(_pair_rows(persistence_pairs))

    simplified_contour_tree = simplify_tree_by_persistence(
        contour_tree,
        persistence_pairs,
        threshold=simplify_threshold,
    )
    print(f"\nSimplified contour tree edges (threshold={simplify_threshold}):")
    print(sorted(tuple(sorted(edge)) for edge in simplified_contour_tree.graph.edges()))

    simplified_persistence_pairs = compute_persistence(
        simplified_contour_tree,
        scalar=scalar,
    )
    print("\nSimplified contour tree persistence pairs:")
    print(_pair_rows(simplified_persistence_pairs))

    output_dir.mkdir(parents=True, exist_ok=True)
    original_graph_path = save_graph_plot(
        graph,
        output_dir / "01_original_graph.svg",
        scalar=scalar,
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
    contour_tree_persistence_path = save_persistence_diagram(
        persistence_pairs,
        output_dir / "05_contour_tree_persistence.svg",
        graph=ordered_graph,
        scalar=scalar,
        title="Contour Tree Persistence",
    )
    simplified_contour_tree_path = save_tree_plot(
        simplified_contour_tree,
        output_dir / "06_simplified_contour_tree.svg",
        title=f"Simplified Contour Tree (threshold={simplify_threshold})",
    )
    simplified_contour_tree_persistence_path = save_persistence_diagram(
        simplified_persistence_pairs,
        output_dir / "07_simplified_contour_tree_persistence.svg",
        graph=simplified_contour_tree.graph,
        scalar=scalar,
        title="Simplified Contour Tree Persistence",
    )
    print("\nWrote SVG plots:")
    print(
        [
            original_graph_path.name,
            split_tree_path.name,
            join_tree_path.name,
            contour_tree_path.name,
            contour_tree_persistence_path.name,
            simplified_contour_tree_path.name,
            simplified_contour_tree_persistence_path.name,
        ]
    )


def _pair_rows(pairs: list[Any]) -> list[tuple[Any, Any, float, str]]:
    """Return printable persistence-pair rows."""

    return [
        (pair.extremum, pair.saddle, pair.persistence, pair.kind)
        for pair in pairs
    ]
