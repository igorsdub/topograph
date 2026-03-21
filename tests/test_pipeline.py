"""Tests for the end-to-end topographer pipeline."""

from __future__ import annotations

import networkx as nx

from topographer.api import run_pipeline


def make_pipeline_graph() -> nx.Graph:
    """Create a small graph with deterministic simplification behavior."""

    graph = nx.Graph()
    graph.add_edges_from([(0, 1), (0, 2), (0, 3)])
    nx.set_node_attributes(graph, {0: 0.0, 1: 3.0, 2: 1.0, 3: 2.0}, "height")
    return graph


def test_run_pipeline_returns_consistent_outputs() -> None:
    graph = make_pipeline_graph()

    result = run_pipeline(graph, scalar="height", simplify_threshold=1.5)

    assert result.graph is graph
    assert result.scalar == "height"
    assert result.ordered_graph is not graph
    assert result.ordered_graph.number_of_nodes() == graph.number_of_nodes()
    assert result.join_tree.graph.number_of_nodes() == graph.number_of_nodes()
    assert result.split_tree.graph.number_of_nodes() == graph.number_of_nodes()
    assert result.contour_tree.graph.number_of_nodes() <= graph.number_of_nodes()
    assert [pair.persistence for pair in result.persistence_pairs] == [2.0, 1.0]
    assert result.simplified_contour_tree is not None
    assert result.simplified_contour_tree.graph.number_of_nodes() == 2
    assert result.simplified_contour_tree.graph.number_of_edges() == 1


def test_run_pipeline_without_simplification_leaves_optional_output_empty() -> None:
    result = run_pipeline(make_pipeline_graph(), scalar="height")

    assert result.simplified_contour_tree is None
