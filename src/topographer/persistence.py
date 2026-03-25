"""Persistence pair computation for merge trees and contour trees."""

from __future__ import annotations

from numbers import Real
from typing import Any, Hashable, Iterable

import networkx as nx

from .core import UnionFind
from .models import ContourTree, MergeTree, PersistencePair

Node = Hashable

__all__ = [
    "compute_persistence",
    "compute_persistence_pairs",
    "persistence_pairs",
]


def _scalar_value(data: dict[str, Any], scalar: str) -> float:
    value = data[scalar]
    if not isinstance(value, Real) or isinstance(value, bool):
        raise TypeError(f"Scalar attribute '{scalar}' must be numeric.")
    return float(value)


def _validate_tree_graph(graph: nx.Graph, scalar: str) -> dict[Node, float]:
    if not isinstance(graph, nx.Graph):
        raise TypeError("tree.graph must be an instance of networkx.Graph.")

    missing = [node for node, data in graph.nodes(data=True) if scalar not in data]
    if missing:
        raise ValueError(f"Missing scalar attribute '{scalar}' on nodes: {missing!r}")

    return {node: _scalar_value(data, scalar) for node, data in graph.nodes(data=True)}


def _ordered_nodes(graph: nx.Graph, scalar: str, *, ascending: bool) -> list[Node]:
    nodes = list(graph.nodes)
    nodes.sort(
        key=lambda node: (_scalar_value(graph.nodes[node], scalar), repr(node)),
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
    scalar_map = _validate_tree_graph(tree.graph, tree.scalar)
    ascending = tree.kind != "split"
    ordered_nodes = _ordered_nodes(tree.graph, tree.scalar, ascending=ascending)

    uf = UnionFind()
    active: set[Node] = set()
    birth: dict[Node, Node] = {}
    pairs: list[PersistencePair] = []
    prefer_low = ascending

    for node in ordered_nodes:
        uf.add(node)
        active_neighbors = [neighbor for neighbor in tree.graph.neighbors(node) if neighbor in active]
        roots = {uf.find(neighbor) for neighbor in active_neighbors}

        if not roots:
            birth[node] = node
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


def persistence_pairs(tree: MergeTree | ContourTree) -> list[PersistencePair]:
    """Compute persistence pairs from a merge tree or contour tree."""

    if isinstance(tree, ContourTree):
        if tree.join_tree is not None and tree.split_tree is not None:
            pairs = _pairs_from_merge_tree(tree.join_tree)
            pairs.extend(_pairs_from_merge_tree(tree.split_tree))
        else:
            pairs = _pairs_from_merge_tree(MergeTree(graph=tree.graph, scalar=tree.scalar, kind="join"))
            pairs.extend(
                _pairs_from_merge_tree(MergeTree(graph=tree.graph, scalar=tree.scalar, kind="split"))
            )
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


def compute_persistence(
    tree: MergeTree | ContourTree,
    scalar: str | None = None,
) -> list[PersistencePair]:
    """Compute deterministic persistence pairs.

    The optional ``scalar`` argument is accepted for compatibility with the
    package roadmap. When provided, it must match the tree scalar name.
    """

    if scalar is not None and scalar != tree.scalar:
        raise ValueError("Requested scalar does not match tree.scalar.")
    return persistence_pairs(tree)


def compute_persistence_pairs(tree: MergeTree | ContourTree) -> list[PersistencePair]:
    """Backward-compatible alias for :func:`compute_persistence`."""

    return compute_persistence(tree)
