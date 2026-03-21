"""Tests for graph validation, ordering, and component tracking."""

from __future__ import annotations

import networkx as nx
import pytest

from topographer.core import (
    UnionFind,
    check_graph,
    ensure_total_order,
    has_unique_scalars,
    make_total_ordering,
)


def make_scalar_graph(values: dict[int, object]) -> nx.Graph:
    """Build a small graph with scalar values on every node."""

    graph = nx.path_graph(len(values))
    nx.set_node_attributes(graph, values, "height")
    return graph


def test_check_graph_rejects_invalid_graph_type() -> None:
    with pytest.raises(TypeError):
        check_graph([], "height")  # type: ignore[arg-type]


def test_check_graph_rejects_missing_scalar() -> None:
    graph = nx.path_graph(3)
    graph.nodes[0]["height"] = 0.0
    graph.nodes[1]["height"] = 1.0

    with pytest.raises(KeyError):
        check_graph(graph, "height")


def test_check_graph_rejects_non_numeric_scalar() -> None:
    graph = nx.path_graph(2)
    nx.set_node_attributes(graph, {0: 0.0, 1: "high"}, "height")

    with pytest.raises(TypeError):
        check_graph(graph, "height")


def test_check_graph_returns_scalar_map() -> None:
    graph = nx.path_graph(3)
    nx.set_node_attributes(graph, {0: 1.0, 1: 2.0, 2: 3.0}, "height")

    assert check_graph(graph, "height") == {0: 1.0, 1: 2.0, 2: 3.0}


def test_check_graph_can_enforce_connectedness() -> None:
    graph = nx.Graph()
    graph.add_nodes_from([0, 1])
    nx.set_node_attributes(graph, {0: 0.0, 1: 1.0}, "height")

    with pytest.raises(ValueError):
        check_graph(graph, "height", require_connected=True)

    assert check_graph(graph, "height", require_connected=False) == {0: 0.0, 1: 1.0}


def test_has_unique_scalars_detects_duplicates() -> None:
    graph = make_scalar_graph({0: 1.0, 1: 1.0, 2: 2.0})

    assert not has_unique_scalars(graph, "height")


def test_ensure_total_order_breaks_ties_deterministically() -> None:
    graph = nx.path_graph(3)
    nx.set_node_attributes(graph, {0: 1.0, 1: 1.0, 2: 2.0}, "height")

    ordered_graph, ordered_scalar = ensure_total_order(graph, "height")

    assert graph.nodes[0]["height"] == 1.0
    assert graph.nodes[1]["height"] == 1.0
    assert graph.nodes[2]["height"] == 2.0
    assert ordered_scalar == {
        0: 1.0,
        1: 1.000000001,
        2: 2.000000002,
    }
    assert [ordered_graph.nodes[node]["height"] for node in ordered_graph.nodes] == [
        1.0,
        1.000000001,
        2.000000002,
    ]


def test_make_total_ordering_can_write_to_new_attribute() -> None:
    graph = make_scalar_graph({0: 1.0, 1: 1.0, 2: 2.0})

    ordered = make_total_ordering(graph, "height", out_attr="ordered_height", inplace=False)

    assert "ordered_height" in ordered.nodes[0]
    assert graph.nodes[0]["height"] == 1.0
    assert len({ordered.nodes[node]["ordered_height"] for node in ordered.nodes}) == 3


def test_union_find_tracks_components() -> None:
    uf = UnionFind([0, 1, 2])

    assert uf.find(0) == 0
    assert uf.union(0, 1) == 0
    assert uf.find(1) == 0
    assert uf.union(0, 2) == 0
    assert uf.components()[0] == {0, 1, 2}
