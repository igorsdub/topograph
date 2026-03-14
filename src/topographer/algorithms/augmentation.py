from __future__ import annotations

"""Tree augmentation helpers from stored arc-vertex traces."""

from collections.abc import Hashable
from typing import Any

import networkx as nx

from topographer.models.tree import ContourTree, MergeTree


def augment_tree_from_arc_vertices(
    arc_vertices: dict[tuple[Hashable, Hashable], list[Hashable]],
) -> nx.Graph[Any]:
    """Expand compressed arcs into an explicit vertex-by-vertex graph."""
    augmented_tree: nx.Graph[Any] = nx.Graph()

    for path in arc_vertices.values():
        if not path:
            continue

        if len(path) == 1:
            augmented_tree.add_node(path[0])
            continue

        for index in range(len(path) - 1):
            augmented_tree.add_edge(path[index], path[index + 1])

    return augmented_tree


def augment_join_tree(result: MergeTree) -> MergeTree:
    """Return a join tree whose graph contains all intermediate arc vertices."""
    if result.kind != "join":
        raise ValueError("augment_join_tree expects a join merge tree")

    augmented_tree = augment_tree_from_arc_vertices(result.arc_vertices)

    return MergeTree(
        graph=augmented_tree,
        root=result.root,
        critical_nodes=result.critical_nodes,
        scalar=result.scalar,
        kind=result.kind,
        augmented=True,
        arc_vertices=result.arc_vertices,
        node_metadata=result.node_metadata,
    )


def augment_split_tree(result: MergeTree) -> MergeTree:
    """Return a split tree whose graph contains all intermediate arc vertices."""
    if result.kind != "split":
        raise ValueError("augment_split_tree expects a split merge tree")

    augmented_tree = augment_tree_from_arc_vertices(result.arc_vertices)

    return MergeTree(
        graph=augmented_tree,
        root=result.root,
        critical_nodes=result.critical_nodes,
        scalar=result.scalar,
        kind=result.kind,
        augmented=True,
        arc_vertices=result.arc_vertices,
        node_metadata=result.node_metadata,
    )


def augment_contour_tree(result: ContourTree) -> ContourTree:
    """Return a contour tree whose graph contains all intermediate arc vertices."""
    augmented_tree = augment_tree_from_arc_vertices(result.arc_vertices)

    return ContourTree(
        graph=augmented_tree,
        scalar=result.scalar,
        split_tree=result.split_tree,
        join_tree=result.join_tree,
        augmented=True,
        critical_nodes=result.critical_nodes,
        arc_vertices=result.arc_vertices,
        node_metadata=result.node_metadata,
    )


__all__ = [
    "augment_tree_from_arc_vertices",
    "augment_join_tree",
    "augment_split_tree",
    "augment_contour_tree",
]
