from __future__ import annotations

from collections.abc import Hashable
from typing import Any

import networkx as nx

from topographer.models.split_join import JoinTreeResult, SplitTreeResult


def augment_tree_from_arc_vertices(
    arc_vertices: dict[tuple[Hashable, Hashable], list[Hashable]],
) -> nx.Graph[Any]:
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


def augment_join_tree(result: JoinTreeResult) -> JoinTreeResult:
    augmented_tree = augment_tree_from_arc_vertices(result.arc_vertices)

    return JoinTreeResult(
        tree=augmented_tree,
        root=result.root,
        critical_nodes=result.critical_nodes,
        scalar=result.scalar,
        augmented=True,
        arc_vertices=result.arc_vertices,
    )


def augment_split_tree(result: SplitTreeResult) -> SplitTreeResult:
    augmented_tree = augment_tree_from_arc_vertices(result.arc_vertices)

    return SplitTreeResult(
        tree=augmented_tree,
        root=result.root,
        critical_nodes=result.critical_nodes,
        scalar=result.scalar,
        augmented=True,
        arc_vertices=result.arc_vertices,
    )


__all__ = ["augment_tree_from_arc_vertices", "augment_join_tree", "augment_split_tree"]
