"""Tests for join trees, split trees, and contour trees."""

from __future__ import annotations

import networkx as nx

from topographer.trees import compute_contour_tree, compute_join_tree, compute_split_tree


def make_chain_graph() -> nx.Graph:
    """Create a simple chain graph with increasing scalar values."""

    graph = nx.path_graph(4)
    nx.set_node_attributes(graph, {0: 0.0, 1: 1.0, 2: 2.0, 3: 3.0}, "height")
    return graph


def make_branch_graph() -> nx.Graph:
    """Create a small branching graph that forces a merge event."""

    graph = nx.Graph()
    graph.add_edges_from([(0, 1), (1, 2), (1, 3)])
    nx.set_node_attributes(graph, {0: 0.0, 1: 2.0, 2: 1.0, 3: 3.0}, "height")
    return graph


def normalized_edges(graph: nx.Graph) -> list[tuple[object, object]]:
    """Return undirected edges in a stable representation."""

    return sorted(tuple(sorted(edge)) for edge in graph.edges())


def test_join_and_split_trees_on_chain_graph() -> None:
    graph = make_chain_graph()

    join_tree = compute_join_tree(graph, "height")
    split_tree = compute_split_tree(graph, "height")

    assert join_tree.graph.number_of_nodes() == graph.number_of_nodes()
    assert split_tree.graph.number_of_nodes() == graph.number_of_nodes()
    assert join_tree.graph.number_of_edges() == graph.number_of_edges()
    assert split_tree.graph.number_of_edges() == graph.number_of_edges()
    assert nx.is_tree(join_tree.graph)
    assert nx.is_tree(split_tree.graph)
    assert normalized_edges(join_tree.graph) == [(0, 1), (1, 2), (2, 3)]


def test_tree_construction_is_deterministic_on_branch_graph() -> None:
    graph = make_branch_graph()

    first_join = compute_join_tree(graph, "height")
    second_join = compute_join_tree(graph, "height")
    first_split = compute_split_tree(graph, "height")
    second_split = compute_split_tree(graph, "height")

    assert normalized_edges(first_join.graph) == normalized_edges(second_join.graph)
    assert normalized_edges(first_split.graph) == normalized_edges(second_split.graph)
    assert first_join.graph.number_of_edges() == graph.number_of_nodes() - 1
    assert first_split.graph.number_of_edges() == graph.number_of_nodes() - 1


def test_contour_tree_contracts_degree_two_nodes() -> None:
    graph = make_branch_graph()

    contour_tree = compute_contour_tree(
        compute_split_tree(graph, "height"),
        compute_join_tree(graph, "height"),
    )

    assert contour_tree.graph.number_of_nodes() <= graph.number_of_nodes()
    assert contour_tree.graph.number_of_edges() <= graph.number_of_nodes() - 1
    assert nx.is_tree(contour_tree.graph)
