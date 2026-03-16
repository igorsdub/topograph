"""Merge split and join trees into a combined contour-tree skeleton."""

from __future__ import annotations

from collections.abc import Hashable

import networkx as nx

from topographer.models.tree import MergeTree


def _edge_key(a: Hashable, b: Hashable) -> tuple[Hashable, Hashable]:
    """Return canonical undirected edge key for map indexing."""
    ordered = sorted((a, b), key=repr)
    return ordered[0], ordered[1]


def _canonicalize_path(path: list[Hashable]) -> list[Hashable]:
    """Choose deterministic orientation for an undirected path."""
    if len(path) <= 1:
        return path

    reversed_path = list(reversed(path))
    if tuple(map(repr, path)) <= tuple(map(repr, reversed_path)):
        return path

    return reversed_path


def merge_split_join_trees(
    ST: MergeTree,
    JT: MergeTree,
) -> tuple[nx.Graph, dict[tuple[Hashable, Hashable], list[Hashable]]]:
    """Merge split and join tree edges and reconcile arc vertex paths.

    For duplicate edges present in both trees, the longer recorded arc path is
    retained as a richer trace of original graph vertices.
    """
    if ST.scalar != JT.scalar:
        raise ValueError("Split tree and join tree must use the same scalar attribute")

    merged_tree = nx.Graph()
    merged_tree.add_nodes_from(ST.tree.nodes())
    merged_tree.add_nodes_from(JT.tree.nodes())

    edge_support: dict[tuple[Hashable, Hashable], int] = {}
    merged_arc_vertices: dict[tuple[Hashable, Hashable], list[Hashable]] = {}

    for source_graph, source_arcs in ((ST.tree, ST.arc_vertices), (JT.tree, JT.arc_vertices)):
        for edge in source_graph.edges():
            key = _edge_key(edge[0], edge[1])
            edge_support[key] = edge_support.get(key, 0) + 1

        for edge, path in source_arcs.items():
            key = _edge_key(edge[0], edge[1])
            canonical_path = _canonicalize_path(path)

            existing = merged_arc_vertices.get(key)
            if existing is None or len(canonical_path) > len(existing):
                merged_arc_vertices[key] = canonical_path

    for edge in edge_support:
        if edge not in merged_arc_vertices:
            merged_arc_vertices[edge] = [edge[0], edge[1]]

    ranked_edges = sorted(
        edge_support,
        key=lambda edge: (
            edge_support[edge],
            len(merged_arc_vertices.get(edge, [edge[0], edge[1]])),
            repr(edge[0]),
            repr(edge[1]),
        ),
        reverse=True,
    )

    uf = nx.utils.UnionFind()

    for node in merged_tree.nodes():
        uf[node]

    for edge in ranked_edges:
        a, b = edge
        if uf[a] == uf[b]:
            continue
        merged_tree.add_edge(a, b)
        uf.union(a, b)

    merged_arc_vertices = {
        key: merged_arc_vertices[key]
        for key in list(merged_arc_vertices.keys())
        if merged_tree.has_edge(*key)
    }

    for edge in merged_tree.edges():
        key = _edge_key(edge[0], edge[1])
        merged_arc_vertices.setdefault(key, [key[0], key[1]])

    return merged_tree, merged_arc_vertices


__all__ = ["merge_split_join_trees"]
