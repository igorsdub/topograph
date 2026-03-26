"""Tests for contour-tree simplification."""

from __future__ import annotations

import networkx as nx

from topographer.persistence import compute_persistence_pairs
from topographer.simplify import simplify_contour_tree, simplify_tree_by_persistence
from topographer.trees import compute_contour_tree, compute_join_tree, compute_split_tree


def make_branch_graph() -> nx.Graph:
    """Create a small cycle graph whose contour tree simplifies cleanly."""

    graph = nx.cycle_graph(4)
    nx.set_node_attributes(graph, {0: 0.0, 1: 3.0, 2: 1.0, 3: 2.0}, "height")
    return graph


def test_threshold_zero_keeps_the_contour_tree_unchanged() -> None:
    graph = make_branch_graph()
    contour_tree = compute_contour_tree(
        compute_split_tree(graph, "height"),
        compute_join_tree(graph, "height"),
    )
    pairs = compute_persistence_pairs(contour_tree)

    simplified = simplify_contour_tree(contour_tree, pairs, threshold=0.0)

    assert simplified.graph.number_of_nodes() == contour_tree.graph.number_of_nodes()
    assert simplified.graph.number_of_edges() == contour_tree.graph.number_of_edges()
    assert sorted(simplified.graph.edges()) == sorted(contour_tree.graph.edges())
    assert simplified.node_metadata == {
        node: dict(simplified.graph.nodes[node]) for node in simplified.graph.nodes
    }


def test_simplify_alias_matches_primary_helper() -> None:
    graph = make_branch_graph()
    contour_tree = compute_contour_tree(
        compute_split_tree(graph, "height"),
        compute_join_tree(graph, "height"),
    )
    pairs = compute_persistence_pairs(contour_tree)

    alias_result = simplify_tree_by_persistence(contour_tree, pairs, threshold=1.5)
    primary_result = simplify_contour_tree(contour_tree, pairs, threshold=1.5)

    assert alias_result.scalar == primary_result.scalar
    assert sorted(alias_result.graph.nodes()) == sorted(primary_result.graph.nodes())
    assert sorted(alias_result.graph.edges()) == sorted(primary_result.graph.edges())


def test_threshold_removes_low_persistence_features() -> None:
    graph = make_branch_graph()
    contour_tree = compute_contour_tree(
        compute_split_tree(graph, "height"),
        compute_join_tree(graph, "height"),
    )
    pairs = compute_persistence_pairs(contour_tree)

    simplified = simplify_contour_tree(contour_tree, pairs, threshold=1.5)

    assert simplified.graph.number_of_nodes() < contour_tree.graph.number_of_nodes()
    assert simplified.graph.number_of_edges() < contour_tree.graph.number_of_edges()
    assert simplified.scalar == contour_tree.scalar
    assert simplified.node_metadata == {
        node: dict(simplified.graph.nodes[node]) for node in simplified.graph.nodes
    }
    assert all(
        simplified.graph.nodes[node]["node_type"] in {"min", "max", "sad", "reg"}
        for node in simplified.graph.nodes
    )


def test_high_threshold_removes_most_features() -> None:
    graph = make_branch_graph()
    contour_tree = compute_contour_tree(
        compute_split_tree(graph, "height"),
        compute_join_tree(graph, "height"),
    )
    pairs = compute_persistence_pairs(contour_tree)

    simplified = simplify_contour_tree(contour_tree, pairs, threshold=10.0)

    assert simplified.graph.number_of_nodes() == 0
    assert simplified.graph.number_of_edges() == 0
    assert simplified.arc_metadata["simplify_threshold"] == 10.0
