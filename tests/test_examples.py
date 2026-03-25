"""Tests for deterministic example graph builders."""

from __future__ import annotations

import networkx as nx

from topographer import (
    make_balanced_tree_graph,
    make_cave_man_graph,
    make_circular_graph,
    make_cubical_graph,
    make_ladder_graph,
    make_path_graph,
    make_star_graph,
    make_tadpole_graph,
    make_trivial_graph,
    make_wheel_graph,
    make_windmill_graph,
)


def test_example_graph_builders_return_graphs_with_bounded_scalars() -> None:
    builders = [
        make_trivial_graph,
        make_path_graph,
        make_circular_graph,
        make_star_graph,
        make_tadpole_graph,
        make_wheel_graph,
        make_cubical_graph,
        make_windmill_graph,
        make_cave_man_graph,
        make_ladder_graph,
        make_balanced_tree_graph,
    ]

    for builder in builders:
        graph = builder()

        assert isinstance(graph, nx.Graph)
        assert graph.number_of_nodes() > 0
        assert nx.is_connected(graph)

        scalar_values = [graph.nodes[node]["scalar"] for node in graph.nodes]
        assert all(0.0 <= value <= 1.0 for value in scalar_values)


def test_path_graph_example_builder_is_deterministic() -> None:
    first_graph = make_path_graph()
    second_graph = make_path_graph()

    assert set(first_graph.edges()) == set(second_graph.edges())
    assert {
        node: first_graph.nodes[node]["scalar"]
        for node in first_graph.nodes
    } == {
        node: second_graph.nodes[node]["scalar"]
        for node in second_graph.nodes
    }
