"""Simplification utilities for contour trees."""

from __future__ import annotations

from collections.abc import Iterable

import networkx as nx

from topographer.models import ContourTree, PersistencePair


def simplify_contour_tree(
    contour_tree: ContourTree,
    persistence_pairs: Iterable[PersistencePair],
    threshold: float,
) -> ContourTree:
    """Remove contour-tree arcs whose attached persistence is below ``threshold``.

    The simplification is intentionally conservative: only edges with explicit
    persistence metadata are removed, and the resulting graph is compressed again
    by removing degree-2 relay vertices.
    """

    simplified_graph = contour_tree.graph.copy()
    edge_persistence: dict[frozenset[object], float] = {}

    for pair in persistence_pairs:
        try:
            path = nx.shortest_path(simplified_graph, pair.birth, pair.death)
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            continue

        for left, right in zip(path, path[1:]):
            key = frozenset((left, right))
            current = edge_persistence.get(key)
            if current is None or pair.persistence < current:
                edge_persistence[key] = pair.persistence

    removable_edges = [
        (u, v)
        for u, v in simplified_graph.edges()
        if edge_persistence.get(frozenset((u, v)), float("inf")) < threshold
    ]
    simplified_graph.remove_edges_from(removable_edges)

    isolated_nodes = [node for node in simplified_graph.nodes if simplified_graph.degree(node) == 0]
    simplified_graph.remove_nodes_from(isolated_nodes)

    changed = True
    while changed:
        changed = False
        for node in list(simplified_graph.nodes):
            if simplified_graph.degree(node) != 2:
                continue

            neighbors = list(simplified_graph.neighbors(node))
            if len(neighbors) != 2 or neighbors[0] == neighbors[1]:
                continue

            if simplified_graph.has_edge(neighbors[0], neighbors[1]):
                simplified_graph.remove_node(node)
            else:
                simplified_graph.add_edge(neighbors[0], neighbors[1])
                simplified_graph.remove_node(node)
            changed = True
            break

    arc_metadata = dict(contour_tree.arc_metadata)
    arc_metadata["simplify_threshold"] = threshold

    return ContourTree(
        graph=simplified_graph,
        scalar=contour_tree.scalar,
        join_tree=None,
        split_tree=None,
        arc_metadata=arc_metadata,
    )


def simplify_tree_by_persistence(
    tree: ContourTree,
    pairs: Iterable[PersistencePair],
    threshold: float,
) -> ContourTree:
    """Compatibility wrapper for persistence-based contour-tree simplification."""

    return simplify_contour_tree(tree, pairs, threshold)
