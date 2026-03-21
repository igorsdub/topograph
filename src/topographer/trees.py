"""Sweep-based split tree, join tree, and contour tree construction.

The implementation is intentionally small and deterministic. It follows a
simple filtration-style sweep over scalar values on nodes and uses a plain
union-find structure to track connected components.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from numbers import Real
from typing import Any, Hashable, Iterable

import networkx as nx

try:  # pragma: no cover - prefer the shared package models when available.
    from .models import ContourTree, MergeTree
except ImportError:  # pragma: no cover - local fallback for this module.

    @dataclass(slots=True)
    class MergeTree:
        """Minimal merge tree container.

        Attributes:
            graph: The tree topology.
            scalar: Name of the node scalar attribute.
            kind: Either ``"join"`` or ``"split"``.
            arc_metadata: Optional per-edge metadata keyed by ``(u, v)``.
        """

        graph: nx.Graph
        scalar: str
        kind: str = ""
        arc_metadata: dict[tuple[Hashable, Hashable], dict[str, Any]] = field(
            default_factory=dict
        )

    @dataclass(slots=True)
    class ContourTree:
        """Minimal contour tree container."""

        graph: nx.Graph
        scalar: str
        join_tree: MergeTree
        split_tree: MergeTree
        arc_metadata: dict[tuple[Hashable, Hashable], dict[str, Any]] = field(
            default_factory=dict
        )


try:  # pragma: no cover - prefer shared core helpers when available.
    from .core import check_graph
except ImportError:  # pragma: no cover - local fallback for this module.

    def check_graph(G: nx.Graph, scalar_attr: str) -> None:
        """Validate that ``G`` is a NetworkX graph with numeric node scalars."""

        if not isinstance(G, nx.Graph):
            raise TypeError("G must be an instance of networkx.Graph.")
        missing = [node for node, data in G.nodes(data=True) if scalar_attr not in data]
        if missing:
            raise ValueError(
                f"Missing scalar attribute '{scalar_attr}' on nodes: {missing!r}"
            )
        bad = [
            node
            for node, data in G.nodes(data=True)
            if not isinstance(data[scalar_attr], Real) or isinstance(data[scalar_attr], bool)
        ]
        if bad:
            raise TypeError(
                f"Scalar attribute '{scalar_attr}' must be numeric on nodes: {bad!r}"
            )


Node = Hashable

__all__ = [
    "MergeTree",
    "ContourTree",
    "join_tree",
    "split_tree",
    "contour_tree",
    "compute_join_tree",
    "compute_split_tree",
    "compute_contour_tree",
]


@dataclass(slots=True)
class _UnionFind:
    """Very small union-find helper used by the sweep."""

    parent: dict[Node, Node] = field(default_factory=dict)

    def add(self, node: Node) -> None:
        """Register ``node`` if it has not been seen before."""

        if node not in self.parent:
            self.parent[node] = node

    def find(self, node: Node) -> Node:
        """Return the current representative for ``node``."""

        parent = self.parent[node]
        if parent != node:
            self.parent[node] = self.find(parent)
        return self.parent[node]

    def union(self, root: Node, other: Node) -> Node:
        """Attach ``other`` under ``root`` and return the surviving root."""

        self.add(root)
        self.add(other)
        root = self.find(root)
        other = self.find(other)
        if root == other:
            return root
        self.parent[other] = root
        return root


def _scalar_value(data: dict[str, Any], scalar: str) -> float:
    value = data[scalar]
    if not isinstance(value, Real) or isinstance(value, bool):
        raise TypeError(f"Scalar attribute '{scalar}' must be numeric.")
    return float(value)


def _ordered_nodes(G: nx.Graph, scalar: str, ascending: bool) -> list[Node]:
    """Return graph nodes in deterministic scalar order."""

    nodes = list(G.nodes)
    nodes.sort(
        key=lambda node: (
            _scalar_value(G.nodes[node], scalar),
            repr(node),
        ),
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


def _build_merge_tree(G: nx.Graph, scalar: str, ascending: bool) -> MergeTree:
    """Build either a join tree or a split tree by sweeping scalar order."""

    check_graph(G, scalar)

    scalar_map = _node_scalar_map(G, scalar)
    ordered_nodes = _ordered_nodes(G, scalar, ascending=ascending)

    tree = nx.Graph()
    tree.add_nodes_from((node, {scalar: scalar_map[node]}) for node in G.nodes)

    uf = _UnionFind()
    active: set[Node] = set()
    representative: dict[Node, Node] = {}
    birth: dict[Node, Node] = {}
    arc_metadata: dict[tuple[Node, Node], dict[str, Any]] = {}

    prefer_low = ascending
    event_kind = "join" if ascending else "split"

    for node in ordered_nodes:
        uf.add(node)
        active_neighbors = [nbr for nbr in G.neighbors(node) if nbr in active]
        roots = {uf.find(nbr) for nbr in active_neighbors}

        if not roots:
            birth[node] = node
            representative[node] = node
            active.add(node)
            continue

        roots_in_order = sorted(
            roots,
            key=lambda root: (
                scalar_map[birth[root]],
                repr(root),
            ),
            reverse=not prefer_low,
        )
        survivor = _component_representative(
            roots_in_order,
            birth,
            scalar_map,
            prefer_low=prefer_low,
        )

        for root in roots_in_order:
            rep = representative[root]
            if rep != node:
                tree.add_edge(node, rep)
                arc_metadata[(node, rep)] = {
                    "event": event_kind,
                    "scalar": scalar_map[node],
                    "component_root": root,
                }
            if root != survivor:
                uf.union(survivor, root)

        if node != survivor:
            uf.union(node, survivor)

        birth[node] = birth[survivor]
        representative[node] = node
        active.add(node)

    return MergeTree(graph=tree, scalar=scalar, kind=event_kind, arc_metadata=arc_metadata)


def join_tree(G: nx.Graph, scalar: str = "scalar") -> MergeTree:
    """Compute the join tree using an ascending sweep."""

    return _build_merge_tree(G, scalar, ascending=True)


def split_tree(G: nx.Graph, scalar: str = "scalar") -> MergeTree:
    """Compute the split tree using a descending sweep."""

    return _build_merge_tree(G, scalar, ascending=False)


def contour_tree(split: MergeTree, join: MergeTree) -> ContourTree:
    """Merge split and join trees, then contract degree-2 nodes.

    The public pipeline passes ``split`` first and ``join`` second. For
    resilience, if the arguments arrive swapped we normalize them by ``kind``.
    """

    if split.kind == "join" and join.kind == "split":
        split, join = join, split

    if join.scalar != split.scalar:
        raise ValueError("Join tree and split tree must use the same scalar name.")

    graph = nx.Graph()
    graph.add_nodes_from(join.graph.nodes(data=True))
    graph.add_nodes_from(split.graph.nodes(data=True))
    graph.add_edges_from(join.graph.edges())
    graph.add_edges_from(split.graph.edges())

    arc_metadata: dict[tuple[Node, Node], dict[str, Any]] = {}
    arc_metadata.update(join.arc_metadata)
    arc_metadata.update(split.arc_metadata)

    changed = True
    while changed:
        changed = False
        degree_two_nodes = [
            node for node in list(graph.nodes) if graph.degree[node] == 2
        ]
        for node in degree_two_nodes:
            neighbors = list(graph.neighbors(node))
            if len(neighbors) != 2:
                continue
            left, right = neighbors
            graph.remove_node(node)
            if left != right and not graph.has_edge(left, right):
                graph.add_edge(left, right)
            arc_metadata.pop((left, node), None)
            arc_metadata.pop((node, left), None)
            arc_metadata.pop((right, node), None)
            arc_metadata.pop((node, right), None)
            changed = True

    return ContourTree(
        graph=graph,
        scalar=join.scalar,
        join_tree=join,
        split_tree=split,
        arc_metadata=arc_metadata,
    )


def compute_join_tree(G: nx.Graph, scalar: str = "scalar") -> MergeTree:
    """Alias for :func:`join_tree`."""

    return join_tree(G, scalar=scalar)


def compute_split_tree(G: nx.Graph, scalar: str = "scalar") -> MergeTree:
    """Alias for :func:`split_tree`."""

    return split_tree(G, scalar=scalar)


def compute_contour_tree(join: MergeTree, split: MergeTree) -> ContourTree:
    """Alias for :func:`contour_tree`."""

    return contour_tree(join, split)
