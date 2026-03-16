"""Helpers to deaugment trees by collapsing regular vertices back onto arc endpoints."""

from __future__ import annotations

from collections.abc import Hashable
from typing import Any

import networkx as nx

from topographer.models.tree import ContourTree, MergeTree


def _edge_key(a: Hashable, b: Hashable) -> tuple[Hashable, Hashable]:
    ordered = sorted((a, b), key=repr)
    return ordered[0], ordered[1]


def deaugment_tree_from_arc_vertices(
    arc_vertices: dict[tuple[Hashable, Hashable], list[Hashable]],
) -> nx.Graph[Any]:
    """Rebuild the compact critical-point skeleton from stored arc traces."""
    graph: nx.Graph[Any] = nx.Graph()

    for edge in arc_vertices:
        a, b = edge
        if a == b:
            graph.add_node(a)
            continue

        graph.add_edge(*_edge_key(a, b))

    return graph


def deaugment_merge_tree(tree: MergeTree) -> MergeTree:
    """Collapse an augmented split/join tree to its compact critical skeleton."""
    compact_graph = deaugment_tree_from_arc_vertices(tree.arc_vertices)
    compact_graph.add_nodes_from(tree.critical_nodes)

    return MergeTree(
        graph=compact_graph,
        root=tree.root,
        critical_nodes=list(tree.critical_nodes),
        scalar=tree.scalar,
        kind=tree.kind,
        augmented=False,
        arc_vertices=dict(tree.arc_vertices),
        node_metadata=dict(tree.node_metadata),
    )


def deaugment_contour_tree(tree: ContourTree) -> ContourTree:
    """Collapse an augmented contour tree to its compact critical skeleton."""
    compact_graph = deaugment_tree_from_arc_vertices(tree.arc_vertices)
    compact_graph.add_nodes_from(tree.critical_nodes)

    return ContourTree(
        graph=compact_graph,
        scalar=tree.scalar,
        split_tree=tree.split_tree,
        join_tree=tree.join_tree,
        augmented=False,
        critical_nodes=list(tree.critical_nodes),
        arc_vertices=dict(tree.arc_vertices),
        node_metadata=dict(tree.node_metadata),
    )


__all__ = [
    "deaugment_tree_from_arc_vertices",
    "deaugment_merge_tree",
    "deaugment_contour_tree",
]
