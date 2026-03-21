"""Tests for lightweight plotting data helpers."""

from __future__ import annotations

import networkx as nx

from topographer.persistence import compute_persistence
from topographer.plot import plot_graph, plot_persistence_diagram, plot_tree
from topographer.trees import compute_contour_tree


def make_graph() -> nx.Graph:
    """Create a small graph with stable scalar values."""

    graph = nx.path_graph(3)
    nx.set_node_attributes(graph, {0: 0.0, 1: 2.0, 2: 1.0}, "height")
    return graph


def test_plot_graph_returns_positions_edges_and_nodes() -> None:
    graph = make_graph()

    data = plot_graph(graph, scalar="height")

    assert set(data) == {"positions", "edges", "nodes"}
    assert set(data["nodes"]) == set(graph.nodes)
    assert len(data["positions"]) == graph.number_of_nodes()


def test_plot_tree_uses_tree_graph_and_scalar() -> None:
    contour_tree = compute_contour_tree(make_graph(), "height")

    data = plot_tree(contour_tree)

    assert set(data["nodes"]) == set(contour_tree.graph.nodes)


def test_plot_persistence_diagram_returns_point_data() -> None:
    contour_tree = compute_contour_tree(make_graph(), "height")
    pairs = compute_persistence(contour_tree, scalar="height")

    data = plot_persistence_diagram(pairs)

    assert "points" in data
    assert all(len(point) == 3 for point in data["points"])
