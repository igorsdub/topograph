import networkx as nx
import pytest

from topographer.plotting.layout import assign_planar_layout, planar_layout


def _branching_tree() -> nx.Graph:
    graph = nx.Graph()
    graph.add_node("r", scalar=10.0)
    graph.add_node("a", scalar=6.0)
    graph.add_node("b", scalar=5.0)
    graph.add_node("c", scalar=1.0)
    graph.add_node("d", scalar=2.0)
    graph.add_node("e", scalar=3.0)
    graph.add_node("f", scalar=4.0)
    graph.add_edges_from(
        [
            ("r", "a"),
            ("r", "b"),
            ("a", "c"),
            ("a", "d"),
            ("b", "e"),
            ("b", "f"),
        ]
    )
    return graph


def test_planar_layout_leaf_span_assigns_expected_positions() -> None:
    graph = _branching_tree()

    pos = planar_layout(graph, scalar="scalar")

    assert pos["c"] == (0.0, 1.0)
    assert pos["d"] == (1.0, 2.0)
    assert pos["e"] == (2.0, 3.0)
    assert pos["f"] == (3.0, 4.0)
    assert pos["a"] == (0.5, 6.0)
    assert pos["b"] == (2.5, 5.0)
    assert pos["r"] == (1.5, 10.0)


def test_assign_planar_layout_writes_node_attributes() -> None:
    graph = _branching_tree()

    pos = assign_planar_layout(graph)

    for node, point in pos.items():
        assert graph.nodes[node]["layout_x"] == point[0]
        assert graph.nodes[node]["layout_y"] == point[1]
        assert graph.nodes[node]["pos"] == point


def test_planar_layout_rejects_unknown_x_mode() -> None:
    graph = _branching_tree()

    with pytest.raises(ValueError, match="Unknown x_mode"):
        planar_layout(graph, x_mode="not_supported")


def test_planar_layout_rejects_non_tree_input() -> None:
    graph = nx.cycle_graph(3)
    for node in graph.nodes:
        graph.nodes[node]["scalar"] = float(node)

    with pytest.raises(ValueError, match="connected acyclic"):
        planar_layout(graph)


def test_planar_layout_rejects_missing_scalar() -> None:
    graph = nx.path_graph(3)
    graph.nodes[0]["scalar"] = 0.0
    graph.nodes[1]["scalar"] = 1.0

    with pytest.raises(ValueError, match="Missing scalar attribute"):
        planar_layout(graph)


def test_planar_layout_rejects_missing_root() -> None:
    graph = _branching_tree()

    with pytest.raises(ValueError, match="is not in tree"):
        planar_layout(graph, root="missing")
