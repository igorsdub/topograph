"""Tests for persistence pair computation."""

from __future__ import annotations

import networkx as nx

from topographer.persistence import compute_persistence, compute_persistence_pairs
from topographer.trees import compute_contour_tree, compute_join_tree, compute_split_tree


def make_known_pair_graph() -> nx.Graph:
    """Create a tiny graph with one known join-tree persistence pair."""

    graph = nx.path_graph(3)
    nx.set_node_attributes(graph, {0: 0.0, 1: 2.0, 2: 1.0}, "height")
    return graph


def make_branch_graph() -> nx.Graph:
    """Create a small star-like graph that yields multiple persistence pairs."""

    graph = nx.Graph()
    graph.add_edges_from([(0, 1), (0, 2), (0, 3)])
    nx.set_node_attributes(graph, {0: 0.0, 1: 3.0, 2: 1.0, 3: 2.0}, "height")
    return graph


def test_persistence_pairs_from_join_tree_are_known() -> None:
    graph = make_known_pair_graph()
    join_tree = compute_join_tree(graph, "height")

    pairs = compute_persistence_pairs(join_tree)

    assert [
        (pair.extremum, pair.saddle, pair.persistence, pair.kind) for pair in pairs
    ] == [(2, 1, 1.0, "join")]


def test_compute_persistence_alias_matches_pair_helper() -> None:
    graph = make_known_pair_graph()
    join_tree = compute_join_tree(graph, "height")

    assert compute_persistence(join_tree, scalar="height") == compute_persistence_pairs(join_tree)


def test_persistence_pairs_from_contour_tree_are_sorted() -> None:
    graph = make_branch_graph()
    contour_tree = compute_contour_tree(
        compute_split_tree(graph, "height"),
        compute_join_tree(graph, "height"),
    )

    pairs = compute_persistence_pairs(contour_tree)
    pair_data = [(pair.extremum, pair.saddle, pair.persistence, pair.kind) for pair in pairs]

    assert pair_data == [(3, 0, 2.0, "split"), (2, 0, 1.0, "split")]
    assert [pair.persistence for pair in pairs] == sorted(
        (pair.persistence for pair in pairs),
        reverse=True,
    )
