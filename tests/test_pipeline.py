"""Tests for the minimal topographer pipeline."""

from __future__ import annotations

import networkx as nx
import pytest

from topographer.api import run_pipeline
from topographer.core import check_graph, ensure_total_order
from topographer.persistence import compute_persistence_pairs
from topographer.simplify import simplify_contour_tree
from topographer.trees import compute_contour_tree, compute_join_tree, compute_split_tree


def make_path_graph() -> nx.Graph:
    """Create a tiny deterministic scalar graph."""

    G = nx.path_graph(5)
    values = {0: 0.0, 1: 2.0, 2: 1.0, 3: 3.0, 4: 4.0}
    nx.set_node_attributes(G, values, "height")
    return G


def test_check_graph_rejects_missing_scalar() -> None:
    G = nx.path_graph(3)
    G.nodes[0]["height"] = 0.0
    G.nodes[1]["height"] = 1.0

    with pytest.raises(KeyError):
        check_graph(G, "height")


def test_ensure_total_order_breaks_ties() -> None:
    G = nx.path_graph(3)
    nx.set_node_attributes(G, {0: 1.0, 1: 1.0, 2: 2.0}, "height")

    ordered_graph, ordered_scalar = ensure_total_order(G, "height")
    ordered_values = [ordered_graph.nodes[node]["height"] for node in ordered_graph.nodes]
    assert set(ordered_scalar) == set(G.nodes)
    assert len(ordered_values) == len(set(ordered_values))


def test_split_and_join_trees_cover_all_nodes() -> None:
    G = make_path_graph()

    join_tree = compute_join_tree(G, "height")
    split_tree = compute_split_tree(G, "height")

    assert set(join_tree.graph.nodes) == set(G.nodes)
    assert set(split_tree.graph.nodes) == set(G.nodes)
    assert nx.is_tree(join_tree.graph)
    assert nx.is_tree(split_tree.graph)


def test_contour_tree_and_persistence_are_computable() -> None:
    G = make_path_graph()

    contour_tree = compute_contour_tree(
        compute_join_tree(G, "height"),
        compute_split_tree(G, "height"),
    )
    pairs = compute_persistence_pairs(contour_tree)

    assert set(contour_tree.graph.nodes).issubset(set(G.nodes))
    assert all(pair.persistence >= 0.0 for pair in pairs)


def test_pipeline_returns_all_intermediate_results() -> None:
    result = run_pipeline(make_path_graph(), scalar="height", simplify_threshold=1.5)

    assert result.ordered_graph.number_of_nodes() == 5
    assert result.join_tree.graph.number_of_nodes() == 5
    assert result.split_tree.graph.number_of_nodes() == 5
    assert result.contour_tree.graph.number_of_nodes() >= 2
    assert result.simplified_contour_tree is not None


def test_simplify_contour_tree_preserves_scalar_name() -> None:
    G = make_path_graph()
    contour_tree = compute_contour_tree(
        compute_join_tree(G, "height"),
        compute_split_tree(G, "height"),
    )
    pairs = compute_persistence_pairs(contour_tree)

    simplified = simplify_contour_tree(contour_tree, pairs, threshold=10.0)

    assert simplified.scalar == contour_tree.scalar
