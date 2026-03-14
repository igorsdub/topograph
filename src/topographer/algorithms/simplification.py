from __future__ import annotations

"""Persistence-threshold simplification for split/join/contour trees.

The implementation follows a TTK-style orchestration:
- simplify join tree (JT) by branch pruning,
- simplify split tree (ST) by branch pruning,
- recompute contour tree (CT) from simplified JT/ST.
"""

from collections.abc import Hashable

import networkx as nx

from topographer.algorithms.contour_tree import compute_contour_tree_from_split_join
from topographer.models.tree import ContourTree, MergeTree


def _edge_key(a: Hashable, b: Hashable) -> tuple[Hashable, Hashable]:
    """Return the canonical undirected edge key used in ``arc_vertices`` maps."""
    ordered = sorted((a, b), key=repr)
    return ordered[0], ordered[1]


def _scalar_for_node(tree: MergeTree, node: Hashable) -> float:
    """Fetch scalar metadata for a tree node as ``float``."""
    metadata = tree.node_metadata.get(node)
    if metadata is None or tree.scalar not in metadata:
        raise ValueError(f"Missing scalar metadata for tree node: {node!r}")
    return float(metadata[tree.scalar])


def _orient_path(path: list[Hashable], start: Hashable, end: Hashable) -> list[Hashable]:
    """Orient an arc path so it runs from ``start`` to ``end``."""
    if not path:
        return [start, end]
    if path[0] == start and path[-1] == end:
        return path
    if path[0] == end and path[-1] == start:
        return list(reversed(path))
    raise ValueError(f"Arc path does not connect expected endpoints: {start!r}, {end!r}")


def _get_arc_path(
    arc_vertices: dict[tuple[Hashable, Hashable], list[Hashable]],
    a: Hashable,
    b: Hashable,
) -> list[Hashable]:
    """Get stored arc path for edge ``(a, b)``, falling back to direct endpoints."""
    return list(arc_vertices.get(_edge_key(a, b), [a, b]))


def _lowest_leaf_arc_below_threshold(
    graph: nx.Graph,
    root: Hashable | None,
    tree: MergeTree,
    threshold: float,
) -> tuple[Hashable, Hashable] | None:
    """Pick the lowest-persistence leaf arc with persistence strictly below threshold.

    Returns ``(leaf, neighbor)`` for the selected arc, or ``None`` if no candidate
    satisfies the threshold.
    """
    best: tuple[float, str, str, Hashable, Hashable] | None = None

    for node in graph.nodes():
        if graph.degree(node) != 1 or node == root:
            continue

        neighbor = next(iter(graph.neighbors(node)))
        persistence = abs(_scalar_for_node(tree, node) - _scalar_for_node(tree, neighbor))
        if persistence >= threshold:
            continue

        candidate = (persistence, repr(node), repr(neighbor), node, neighbor)
        if best is None or candidate < best:
            best = candidate

    if best is None:
        return None

    return best[3], best[4]


def _sorted_critical_nodes(tree: MergeTree, graph: nx.Graph) -> list[Hashable]:
    """Sort surviving nodes by scalar in tree-consistent order.

    Join trees sort ascending, split trees sort descending.
    """
    reverse = tree.kind == "split"
    return sorted(
        graph.nodes(),
        key=lambda node: _scalar_for_node(tree, node),
        reverse=reverse,
    )


def _simplify_tree(tree: MergeTree, threshold: float) -> MergeTree:
    """Simplify one split/join tree via iterative leaf-arc pruning.

    At each iteration the algorithm removes the leaf arc with minimum persistence
    below ``threshold``. If the incident saddle becomes degree-2 (and is not root),
    it is contracted by merging the two adjacent arcs and their vertex traces.
    """
    if threshold < 0:
        raise ValueError("Simplification threshold must be non-negative")

    simplified_graph = tree.graph.copy()
    simplified_arc_vertices = {
        edge: list(vertices) for edge, vertices in tree.arc_vertices.items()
    }
    simplified_node_metadata = {
        node: dict(metadata) for node, metadata in tree.node_metadata.items()
    }

    proxy_tree = tree.__class__(
        graph=simplified_graph,
        root=tree.root,
        critical_nodes=list(tree.critical_nodes),
        scalar=tree.scalar,
        kind=tree.kind,
        augmented=tree.augmented,
        arc_vertices=simplified_arc_vertices,
        node_metadata=simplified_node_metadata,
    )

    while True:
        candidate = _lowest_leaf_arc_below_threshold(
            graph=simplified_graph,
            root=tree.root,
            tree=proxy_tree,
            threshold=threshold,
        )
        if candidate is None:
            break

        leaf, saddle = candidate
        simplified_graph.remove_edge(leaf, saddle)
        simplified_arc_vertices.pop(_edge_key(leaf, saddle), None)

        if simplified_graph.degree(saddle) == 2 and saddle != tree.root:
            left, right = tuple(simplified_graph.neighbors(saddle))

            left_path = _orient_path(
                _get_arc_path(simplified_arc_vertices, left, saddle),
                start=left,
                end=saddle,
            )
            right_path = _orient_path(
                _get_arc_path(simplified_arc_vertices, saddle, right),
                start=saddle,
                end=right,
            )

            simplified_arc_vertices.pop(_edge_key(left, saddle), None)
            simplified_arc_vertices.pop(_edge_key(saddle, right), None)

            merged_path = left_path + right_path[1:]
            simplified_graph.remove_node(saddle)
            simplified_graph.add_edge(left, right)
            simplified_arc_vertices[_edge_key(left, right)] = merged_path
            simplified_node_metadata.pop(saddle, None)

        simplified_graph.remove_node(leaf)
        simplified_node_metadata.pop(leaf, None)

    critical_nodes = _sorted_critical_nodes(proxy_tree, simplified_graph)

    return tree.__class__(
        graph=simplified_graph,
        root=tree.root if tree.root in simplified_graph else None,
        critical_nodes=critical_nodes,
        scalar=tree.scalar,
        kind=tree.kind,
        augmented=tree.augmented,
        arc_vertices=simplified_arc_vertices,
        node_metadata=simplified_node_metadata,
    )


def simplify_join_tree(tree: MergeTree, threshold: float) -> MergeTree:
    """Simplify a join tree with a persistence threshold."""
    if tree.kind != "join":
        raise ValueError("simplify_join_tree expects a join merge tree")
    return _simplify_tree(tree, threshold)


def simplify_split_tree(tree: MergeTree, threshold: float) -> MergeTree:
    """Simplify a split tree with a persistence threshold."""
    if tree.kind != "split":
        raise ValueError("simplify_split_tree expects a split merge tree")
    return _simplify_tree(tree, threshold)


def simplify_contour_tree(tree: ContourTree, threshold: float) -> ContourTree:
    """Simplify contour-tree context by simplifying JT/ST, then recomputing CT."""
    if tree.split_tree is None or tree.join_tree is None:
        raise ValueError("Simplifying contour tree requires both split_tree and join_tree context")

    simplified_split = simplify_split_tree(tree.split_tree, threshold=threshold)
    simplified_join = simplify_join_tree(tree.join_tree, threshold=threshold)
    return compute_contour_tree_from_split_join(simplified_split, simplified_join)


__all__ = [
    "simplify_join_tree",
    "simplify_split_tree",
    "simplify_contour_tree",
]
