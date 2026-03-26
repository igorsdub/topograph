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


def _canonical_edge(edge: tuple[Node, Node]) -> tuple[Node, Node]:
    """Return a deterministic undirected edge key."""

    left, right = edge
    return (left, right) if repr(left) <= repr(right) else (right, left)


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


def _merge_arc_metadata(
    *metadata_entries: dict[str, Any] | None,
) -> dict[str, Any]:
    """Combine edge metadata from split and join trees deterministically."""

    merged: dict[str, Any] = {}
    sources: list[str] = []

    for entry in metadata_entries:
        if not entry:
            continue

        event = entry.get("event")
        if isinstance(event, str) and event not in sources:
            sources.append(event)

        for key in ("component_root", "scalar"):
            if key in entry and key not in merged:
                merged[key] = entry[key]

    if len(sources) == 1:
        merged["event"] = sources[0]
    elif sources:
        merged["event"] = "contour"
        merged["sources"] = tuple(sorted(sources))

    return merged


def _contour_critical_nodes(
    contour_node_metadata: dict[Node, dict[str, Any]],
) -> set[Node]:
    """Return nodes that must stay explicit in the contour-tree skeleton."""

    return {
        node
        for node, metadata in contour_node_metadata.items()
        if metadata.get("node_type") != "reg"
    }


def _super_arc_path(
    graph: nx.Graph,
    start: Node,
    neighbor: Node,
    critical_nodes: set[Node],
) -> list[Node]:
    """Follow a maximal chain until the next contour-critical node."""

    path = [start, neighbor]
    previous = start
    current = neighbor

    while current not in critical_nodes:
        next_nodes = [node for node in graph.neighbors(current) if node != previous]
        if not next_nodes:
            break
        previous, current = current, next_nodes[0]
        path.append(current)

    return path


def _reduced_merge_tree(
    tree: MergeTree,
    critical_nodes: set[Node],
) -> tuple[nx.Graph, dict[tuple[Node, Node], list[Node]], dict[tuple[Node, Node], dict[str, Any]]]:
    """Contract non-critical relay nodes into super-arcs."""

    reduced = nx.Graph()
    reduced.add_nodes_from(
        (
            node,
            dict(tree.graph.nodes[node]),
        )
        for node in tree.graph.nodes
        if node in critical_nodes
    )

    arc_paths: dict[tuple[Node, Node], list[Node]] = {}
    arc_metadata: dict[tuple[Node, Node], dict[str, Any]] = {}

    for node in reduced.nodes:
        for neighbor in tree.graph.neighbors(node):
            path = _super_arc_path(tree.graph, node, neighbor, critical_nodes)
            target = path[-1]
            if target == node:
                continue

            edge = _canonical_edge((node, target))
            if edge in arc_paths:
                continue

            reduced.add_edge(*edge)
            arc_paths[edge] = path if edge == (node, target) else list(reversed(path))

            path_edges = [_canonical_edge((left, right)) for left, right in zip(path, path[1:])]
            metadata_entries = [
                tree.arc_metadata.get((left, right))
                or tree.arc_metadata.get((right, left))
                for left, right in zip(path, path[1:])
            ]
            arc_metadata[edge] = _merge_arc_metadata(*metadata_entries)
            arc_metadata[edge]["source_tree"] = tree.kind
            arc_metadata[edge]["path_edges"] = tuple(path_edges)

    return reduced, arc_paths, arc_metadata


def _skeleton_priority(
    tree: MergeTree,
    critical_nodes: set[Node],
) -> tuple[int, int, int]:
    """Score a merge tree by how much critical contour structure it exposes."""

    saddle_count = sum(
        1
        for node in critical_nodes
        if tree.graph.nodes[node].get("saddle_type") is not None
    )
    explicit_count = sum(
        1
        for node in critical_nodes
        if tree.graph.nodes[node].get("node_type") != "reg"
    )
    kind_priority = 1 if tree.kind == "join" else 0
    return saddle_count, explicit_count, kind_priority


def _expanded_contour_graph(
    base_tree: MergeTree,
    contour_node_metadata: dict[Node, dict[str, Any]],
    critical_nodes: set[Node],
) -> tuple[nx.Graph, dict[tuple[Node, Node], dict[str, Any]]]:
    """Expand a chosen contour skeleton back to an augmented contour tree."""

    reduced_graph, arc_paths, reduced_arc_metadata = _reduced_merge_tree(base_tree, critical_nodes)

    graph = nx.Graph()
    graph.add_nodes_from((node, dict(metadata)) for node, metadata in contour_node_metadata.items())

    arc_metadata: dict[tuple[Node, Node], dict[str, Any]] = {}

    for edge in reduced_graph.edges():
        canonical_edge = _canonical_edge(edge)
        path = arc_paths[canonical_edge]
        for left, right in zip(path, path[1:]):
            canonical_path_edge = _canonical_edge((left, right))
            graph.add_edge(left, right)
            arc_metadata[canonical_path_edge] = {
                **reduced_arc_metadata[canonical_edge],
                "critical_arc": canonical_edge,
            }

    return graph, arc_metadata


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

    global_minimum = ordered_nodes[0] if ascending else ordered_nodes[-1]
    global_maximum = ordered_nodes[-1] if ascending else ordered_nodes[0]
    endpoint = global_maximum if ascending else global_minimum
    endpoint_type: NodeType = "max" if ascending else "min"
    tree.nodes[endpoint]["node_type"] = endpoint_type
    tree.nodes[endpoint]["saddle_type"] = None

    node_metadata = _sync_node_metadata(tree)

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
    """Build an augmented contour tree while preserving critical connectivity."""

    if split.kind == "join" and join.kind == "split":
        split, join = join, split

    if join.scalar != split.scalar:
        raise ValueError("Join tree and split tree must use the same scalar name.")

    contour_node_metadata = {
        node: _contour_node_metadata(
            node,
            join.node_metadata.get(node, dict(join.graph.nodes[node])),
            split.node_metadata.get(node, dict(split.graph.nodes[node])),
            join.scalar,
        )
        for node in set(join.graph.nodes) | set(split.graph.nodes)
    }
    critical_nodes = _contour_critical_nodes(contour_node_metadata)
    base_tree = max((join, split), key=lambda tree: _skeleton_priority(tree, critical_nodes))
    graph, arc_metadata = _expanded_contour_graph(base_tree, contour_node_metadata, critical_nodes)

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
