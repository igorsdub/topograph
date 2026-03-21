"""Persistence pair computation for merge trees and contour trees.

This module mirrors the tree sweep logic in a small, deterministic way. The
implementation is intentionally lightweight and depends only on NetworkX plus
the local tree dataclasses.
"""

from __future__ import annotations

from dataclasses import dataclass
from numbers import Real
from typing import Any, Hashable, Iterable

import networkx as nx

try:  # pragma: no cover - prefer shared package models when available.
    from .models import ContourTree, MergeTree, PersistencePair
except ImportError:  # pragma: no cover - local fallbacks for this module.
    from .trees import ContourTree, MergeTree

    @dataclass(slots=True)
    class PersistencePair:
        """Minimal persistence pair container."""

        extremum: Hashable
        saddle: Hashable
        persistence: float
        kind: str


Node = Hashable

__all__ = [
    "PersistencePair",
    "persistence_pairs",
    "compute_persistence_pairs",
]


@dataclass(slots=True)
class _UnionFind:
    """Small union-find helper used to track active components."""

    parent: dict[Node, Node]

    def __init__(self) -> None:
        self.parent = {}

    def add(self, node: Node) -> None:
        if node not in self.parent:
            self.parent[node] = node

    def find(self, node: Node) -> Node:
        parent = self.parent[node]
        if parent != node:
            self.parent[node] = self.find(parent)
        return self.parent[node]

    def union(self, root: Node, other: Node) -> Node:
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


def _validate_graph(graph: nx.Graph, scalar: str) -> dict[Node, float]:
    if not isinstance(graph, nx.Graph):
        raise TypeError("tree.graph must be an instance of networkx.Graph.")
    missing = [node for node, data in graph.nodes(data=True) if scalar not in data]
    if missing:
        raise ValueError(f"Missing scalar attribute '{scalar}' on nodes: {missing!r}")
    return {node: _scalar_value(data, scalar) for node, data in graph.nodes(data=True)}


def _ordered_nodes(
    graph: nx.Graph,
    scalar: str,
    *,
    ascending: bool,
) -> list[Node]:
    nodes = list(graph.nodes)
    nodes.sort(
        key=lambda node: (
            _scalar_value(graph.nodes[node], scalar),
            repr(node),
        ),
        reverse=not ascending,
    )
    return nodes


def _component_representative(
    roots: Iterable[Node],
    birth: dict[Node, Node],
    scalar_map: dict[Node, float],
    *,
    prefer_low: bool,
) -> Node:
    def key(root: Node) -> tuple[float, str]:
        value = scalar_map[birth[root]]
        return (value, repr(root)) if prefer_low else (-value, repr(root))

    return min(roots, key=key)


def _pairs_from_merge_tree(tree: MergeTree) -> list[PersistencePair]:
    scalar_map = _validate_graph(tree.graph, tree.scalar)
    ascending = tree.kind != "split"
    ordered_nodes = _ordered_nodes(tree.graph, tree.scalar, ascending=ascending)

    uf = _UnionFind()
    active: set[Node] = set()
    birth: dict[Node, Node] = {}
    pairs: list[PersistencePair] = []
    prefer_low = ascending

    for node in ordered_nodes:
        uf.add(node)
        active_neighbors = [nbr for nbr in tree.graph.neighbors(node) if nbr in active]
        roots = {uf.find(nbr) for nbr in active_neighbors}

        if not roots:
            birth[node] = node
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
            if root == survivor:
                continue
            extremum = birth[root]
            pairs.append(
                PersistencePair(
                    extremum=extremum,
                    saddle=node,
                    persistence=abs(scalar_map[extremum] - scalar_map[node]),
                    kind=tree.kind or ("join" if ascending else "split"),
                )
            )
            uf.union(survivor, root)

        if node != survivor:
            uf.union(node, survivor)
        birth[node] = birth[survivor]
        active.add(node)

    pairs.sort(
        key=lambda pair: (
            -pair.persistence,
            repr(pair.extremum),
            repr(pair.saddle),
            pair.kind,
        )
    )
    return pairs


def persistence_pairs(
    tree: MergeTree | ContourTree,
) -> list[PersistencePair]:
    """Compute persistence pairs from a merge tree or contour tree."""

    if isinstance(tree, ContourTree):
        pairs = _pairs_from_merge_tree(tree.join_tree)
        pairs.extend(_pairs_from_merge_tree(tree.split_tree))
        pairs.sort(
            key=lambda pair: (
                -pair.persistence,
                repr(pair.extremum),
                repr(pair.saddle),
                pair.kind,
            )
        )
        return pairs
    return _pairs_from_merge_tree(tree)


def compute_persistence_pairs(
    tree: MergeTree | ContourTree,
) -> list[PersistencePair]:
    """Alias for :func:`persistence_pairs`."""

    return persistence_pairs(tree)
