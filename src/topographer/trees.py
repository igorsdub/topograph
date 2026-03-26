"""Sweep-based split tree, join tree, and contour tree construction."""

from __future__ import annotations

from numbers import Real
from typing import Any, Hashable, Iterable

import networkx as nx

from .core import UnionFind, check_graph
from .models import ContourTree, MergeTree, NodeType, SaddleType

Node = Hashable

__all__ = [
    "compute_contour_tree",
    "compute_contour_tree_from_trees",
    "compute_join_tree",
    "compute_split_tree",
    "contour_tree",
    "join_tree",
    "split_tree",
]


def _scalar_value(data: dict[str, Any], scalar: str) -> float:
    value = data[scalar]
    if not isinstance(value, Real) or isinstance(value, bool):
        raise TypeError(f"Scalar attribute '{scalar}' must be numeric.")
    return float(value)


def _ordered_nodes(G: nx.Graph, scalar: str, ascending: bool) -> list[Node]:
    """Return graph nodes in deterministic scalar order."""

    nodes = list(G.nodes)
    nodes.sort(
        key=lambda node: (_scalar_value(G.nodes[node], scalar), repr(node)),
        reverse=not ascending,
    )
    return nodes


def _node_scalar_map(G: nx.Graph, scalar: str) -> dict[Node, float]:
    """Build a plain node-to-scalar mapping."""

    return {node: _scalar_value(data, scalar) for node, data in G.nodes(data=True)}


def _component_representative(
    roots: Iterable[Node],
    birth: dict[Node, Node],
    scalar_map: dict[Node, float],
    *,
    prefer_low: bool,
) -> Node:
    """Choose the surviving component root deterministically."""

    def key(root: Node) -> tuple[float, str]:
        value = scalar_map[birth[root]]
        return (value, repr(root)) if prefer_low else (-value, repr(root))

    return min(roots, key=key)


def _classify_sweep_node(
    roots: set[Node],
    *,
    ascending: bool,
) -> dict[str, NodeType | SaddleType | None]:
    """Classify a node from the local sweep event."""

    if not roots:
        return {
            "node_type": "min" if ascending else "max",
            "saddle_type": None,
        }
    if len(roots) > 1:
        return {
            "node_type": "sad",
            "saddle_type": "join_sad" if ascending else "split_sad",
        }
    return {"node_type": "reg", "saddle_type": None}


def _sync_node_metadata(graph: nx.Graph) -> dict[Node, dict[str, Any]]:
    """Mirror graph node attributes into a plain metadata mapping."""

    return {
        node: dict(data)
        for node, data in graph.nodes(data=True)
    }


def _contour_node_metadata(
    node: Node,
    join_data: dict[str, Any],
    split_data: dict[str, Any],
    scalar: str,
) -> dict[str, Any]:
    """Combine join/split node metadata for a contour-tree node."""

    join_type = join_data.get("node_type")
    split_type = split_data.get("node_type")
    join_saddle = join_data.get("saddle_type")
    split_saddle = split_data.get("saddle_type")

    metadata: dict[str, Any] = {
        scalar: join_data.get(scalar, split_data.get(scalar)),
        "node_type": "reg",
        "saddle_type": None,
    }

    if join_type == "min":
        metadata["node_type"] = "min"
    elif split_type == "max":
        metadata["node_type"] = "max"
    elif join_saddle is not None or split_saddle is not None:
        metadata["node_type"] = "sad"
        if join_saddle is not None and split_saddle is not None:
            metadata["saddle_sources"] = ("join_sad", "split_sad")
        else:
            metadata["saddle_type"] = join_saddle or split_saddle

    return metadata


def _build_merge_tree(G: nx.Graph, scalar: str, ascending: bool) -> MergeTree:
    """Build either a join tree or a split tree by sweeping scalar order."""

    check_graph(G, scalar)

    scalar_map = _node_scalar_map(G, scalar)
    ordered_nodes = _ordered_nodes(G, scalar, ascending=ascending)

    tree = nx.Graph()
    tree.add_nodes_from(
        (
            node,
            {
                scalar: scalar_map[node],
                "node_type": "reg",
                "saddle_type": None,
            },
        )
        for node in G.nodes
    )

    uf = UnionFind()
    active: set[Node] = set()
    representative: dict[Node, Node] = {}
    birth: dict[Node, Node] = {}
    node_metadata: dict[Node, dict[str, Any]] = {}
    arc_metadata: dict[tuple[Node, Node], dict[str, Any]] = {}

    prefer_low = ascending
    event_kind = "join" if ascending else "split"

    for node in ordered_nodes:
        uf.add(node)
        active_neighbors = [neighbor for neighbor in G.neighbors(node) if neighbor in active]
        roots = {uf.find(neighbor) for neighbor in active_neighbors}
        classification = _classify_sweep_node(roots, ascending=ascending)
        tree.nodes[node].update(classification)
        node_metadata[node] = dict(tree.nodes[node])

        if not roots:
            birth[node] = node
            representative[node] = node
            active.add(node)
            continue

        roots_in_order = sorted(
            roots,
            key=lambda root: (scalar_map[birth[root]], repr(root)),
            reverse=not prefer_low,
        )
        survivor = _component_representative(
            roots_in_order,
            birth,
            scalar_map,
            prefer_low=prefer_low,
        )

        for root in roots_in_order:
            representative_node = representative[root]
            if representative_node != node:
                tree.add_edge(node, representative_node)
                arc_metadata[(node, representative_node)] = {
                    "component_root": root,
                    "event": event_kind,
                    "scalar": scalar_map[node],
                }
            if root != survivor:
                uf.union(survivor, root)

        if node != survivor:
            uf.union(node, survivor)

        birth[node] = birth[survivor]
        representative[node] = node
        active.add(node)

    return MergeTree(
        graph=tree,
        scalar=scalar,
        kind=event_kind,
        node_metadata=node_metadata,
        arc_metadata=arc_metadata,
    )


def join_tree(G: nx.Graph, scalar: str = "scalar") -> MergeTree:
    """Compute the join tree using an ascending sweep."""

    return _build_merge_tree(G, scalar, ascending=True)


def split_tree(G: nx.Graph, scalar: str = "scalar") -> MergeTree:
    """Compute the split tree using a descending sweep."""

    return _build_merge_tree(G, scalar, ascending=False)


def contour_tree(split: MergeTree, join: MergeTree) -> ContourTree:
    """Merge split and join trees, then contract degree-2 relay nodes."""

    if split.kind == "join" and join.kind == "split":
        split, join = join, split

    if join.scalar != split.scalar:
        raise ValueError("Join tree and split tree must use the same scalar name.")

    graph = nx.Graph()
    contour_node_metadata = {
        node: _contour_node_metadata(
            node,
            join.node_metadata.get(node, dict(join.graph.nodes[node])),
            split.node_metadata.get(node, dict(split.graph.nodes[node])),
            join.scalar,
        )
        for node in set(join.graph.nodes) | set(split.graph.nodes)
    }
    graph.add_nodes_from((node, dict(metadata)) for node, metadata in contour_node_metadata.items())
    graph.add_edges_from(join.graph.edges())
    graph.add_edges_from(split.graph.edges())

    arc_metadata: dict[tuple[Node, Node], dict[str, Any]] = {}
    arc_metadata.update(join.arc_metadata)
    arc_metadata.update(split.arc_metadata)

    changed = True
    while changed:
        changed = False
        for node in list(graph.nodes):
            if graph.degree[node] != 2:
                continue

            neighbors = list(graph.neighbors(node))
            if len(neighbors) != 2:
                continue

            contour_node_metadata.pop(node, None)
            left, right = neighbors
            graph.remove_node(node)
            if left != right and not graph.has_edge(left, right):
                graph.add_edge(left, right)

            arc_metadata.pop((left, node), None)
            arc_metadata.pop((node, left), None)
            arc_metadata.pop((right, node), None)
            arc_metadata.pop((node, right), None)
            changed = True
            break

    return ContourTree(
        graph=graph,
        scalar=join.scalar,
        join_tree=join,
        split_tree=split,
        node_metadata=_sync_node_metadata(graph),
        arc_metadata=arc_metadata,
    )


def compute_join_tree(G: nx.Graph, scalar: str = "scalar") -> MergeTree:
    """Alias for :func:`join_tree`."""

    return join_tree(G, scalar=scalar)


def compute_split_tree(G: nx.Graph, scalar: str = "scalar") -> MergeTree:
    """Alias for :func:`split_tree`."""

    return split_tree(G, scalar=scalar)


def compute_contour_tree_from_trees(split_tree: MergeTree, join_tree: MergeTree) -> ContourTree:
    """Build a contour tree from precomputed split and join trees."""

    return contour_tree(split_tree, join_tree)


def compute_contour_tree(
    graph_or_split_tree: nx.Graph | MergeTree,
    scalar_or_join_tree: str | MergeTree = "scalar",
) -> ContourTree:
    """Compute a contour tree from a graph or from split/join trees.

    This keeps the public API convenient for direct use while preserving the
    explicit pipeline in :mod:`topographer.api`.
    """

    if isinstance(graph_or_split_tree, nx.Graph):
        scalar = str(scalar_or_join_tree)
        split = compute_split_tree(graph_or_split_tree, scalar=scalar)
        join = compute_join_tree(graph_or_split_tree, scalar=scalar)
        return compute_contour_tree_from_trees(split, join)

    if not isinstance(scalar_or_join_tree, MergeTree):
        raise TypeError(
            "compute_contour_tree expects either (graph, scalar) or "
            "(split_tree, join_tree)."
        )

    return compute_contour_tree_from_trees(graph_or_split_tree, scalar_or_join_tree)
