"""Tests for lightweight plotting data helpers."""

from __future__ import annotations

from pathlib import Path

import networkx as nx

from topographer.models import MergeTree
from topographer.persistence import compute_persistence
from topographer.plot import (
    plot_graph,
    plot_persistence_diagram,
    plot_tree,
    save_graph_plot,
    save_persistence_diagram,
    save_tree_plot,
    scalar_layout,
    write_gallery_html,
)
from topographer.trees import compute_contour_tree


def make_graph() -> nx.Graph:
    """Create a small graph with stable scalar values."""

    graph = nx.path_graph(3)
    nx.set_node_attributes(graph, {0: 0.0, 1: 2.0, 2: 1.0}, "height")
    return graph


def make_positioned_graph() -> nx.Graph:
    """Create a graph with explicit node positions for plotting."""

    graph = make_graph()
    nx.set_node_attributes(
        graph,
        {
            0: (0.0, 0.0),
            1: (1.0, 0.5),
            2: (0.5, 1.0),
        },
        "pos",
    )
    return graph


def make_branching_tree() -> MergeTree:
    """Create a tree with a clear min-to-max trunk and side branches."""

    graph = nx.Graph()
    graph.add_edges_from([(0, 1), (1, 2), (2, 3), (1, 4), (4, 6), (2, 5)])
    nx.set_node_attributes(
        graph,
        {
            0: 0.0,
            1: 1.0,
            2: 2.0,
            3: 3.0,
            4: 1.5,
            5: 2.5,
            6: 1.75,
        },
        "height",
    )
    return MergeTree(graph=graph, scalar="height", kind="join")


def test_plot_graph_returns_positions_edges_and_nodes() -> None:
    graph = make_positioned_graph()

    data = plot_graph(graph, scalar="height")

    assert set(data) == {"positions", "edges", "nodes"}
    assert set(data["nodes"]) == set(graph.nodes)
    assert len(data["positions"]) == graph.number_of_nodes()
    assert data["positions"] == {
        node: tuple(graph.nodes[node]["pos"]) for node in graph.nodes
    }


def test_scalar_layout_uses_scalar_values_for_y_positions() -> None:
    graph = make_graph()

    positions = scalar_layout(graph, scalar="height")

    assert {node: position[0] for node, position in positions.items()} == {
        node: 0.0 for node in graph.nodes
    }
    assert {node: position[1] for node, position in positions.items()} == {
        node: float(graph.nodes[node]["height"]) for node in graph.nodes
    }


def test_plot_tree_uses_tree_graph_and_scalar() -> None:
    contour_tree = compute_contour_tree(make_graph(), "height")

    data = plot_tree(contour_tree)

    assert set(data["nodes"]) == set(contour_tree.graph.nodes)


def test_plot_tree_keeps_scalar_values_on_y_axis() -> None:
    tree = make_branching_tree()

    data = plot_tree(tree)

    assert {node: position[1] for node, position in data["positions"].items()} == {
        node: float(tree.graph.nodes[node]["height"]) for node in tree.graph.nodes
    }


def test_plot_tree_places_trunk_on_center_line() -> None:
    tree = make_branching_tree()

    positions = plot_tree(tree)["positions"]

    for node in [0, 1, 2, 3]:
        assert positions[node][0] == 0.0


def test_plot_tree_places_off_trunk_branches_on_nonzero_sides() -> None:
    tree = make_branching_tree()

    positions = plot_tree(tree)["positions"]

    assert positions[4][0] < 0.0
    assert positions[6][0] < 0.0
    assert positions[5][0] > 0.0


def test_plot_tree_layout_is_deterministic() -> None:
    tree = make_branching_tree()

    first = plot_tree(tree)["positions"]
    second = plot_tree(tree)["positions"]

    assert first == second


def test_plot_tree_falls_back_to_scalar_layout_for_non_tree_graphs() -> None:
    graph = nx.cycle_graph(4)
    nx.set_node_attributes(graph, {0: 0.0, 1: 1.0, 2: 2.0, 3: 3.0}, "height")
    contour_tree = compute_contour_tree(graph, "height")

    data = plot_tree(contour_tree)

    assert set(data["nodes"]) == set(contour_tree.graph.nodes)
    assert all(position[0] == 0.0 for position in data["positions"].values())


def test_plot_persistence_diagram_returns_point_data() -> None:
    contour_tree = compute_contour_tree(make_graph(), "height")
    pairs = compute_persistence(contour_tree, scalar="height")

    data = plot_persistence_diagram(pairs)

    assert "points" in data
    assert all(len(point) == 3 for point in data["points"])


def test_plot_persistence_diagram_can_use_scalar_coordinates() -> None:
    graph = make_graph()
    contour_tree = compute_contour_tree(graph, "height")
    pairs = compute_persistence(contour_tree, scalar="height")

    data = plot_persistence_diagram(pairs, graph=graph, scalar="height")

    assert data["points"] == [(1.0, 2.0, 1.0)]


def test_save_graph_plot_uses_graph_layout_and_colorbar(monkeypatch, tmp_path: Path) -> None:
    graph = make_positioned_graph()

    class FakeAxisVisibility:
        def __init__(self) -> None:
            self.visible = True

        def set_visible(self, value: bool) -> None:
            self.visible = value

    class FakeSpine:
        def __init__(self) -> None:
            self.visible = True

        def set_visible(self, value: bool) -> None:
            self.visible = value

    class FakeAxis:
        def __init__(self) -> None:
            self.title = ""
            self.margins_value = None
            self.axis_off = False

        def set_title(self, title: str) -> None:
            self.title = title

        def set_axis_off(self) -> None:
            self.axis_off = True

        def margins(self, value: float) -> None:
            self.margins_value = value

    class FakeFigure:
        def __init__(self) -> None:
            self.tight_layout_called = False
            self.saved_paths: list[Path] = []
            self.colorbar_calls: list[dict[str, object]] = []

        def tight_layout(self) -> None:
            self.tight_layout_called = True

        def savefig(self, path: Path, dpi: int) -> None:
            self.saved_paths.append(path)
            path.write_text("fake image", encoding="utf-8")

        def colorbar(self, mappable: object, ax: object, label: str) -> None:
            self.colorbar_calls.append({"mappable": mappable, "ax": ax, "label": label})

    class FakePyplot:
        def __init__(self) -> None:
            self.figure = FakeFigure()
            self.axis = FakeAxis()
            self.closed_figures: list[FakeFigure] = []
            self.cm = type("FakeColorMaps", (), {"viridis": object()})()

        def subplots(self, figsize: tuple[float, float]) -> tuple[FakeFigure, FakeAxis]:
            return self.figure, self.axis

        def close(self, figure: FakeFigure) -> None:
            self.closed_figures.append(figure)

    fake_pyplot = FakePyplot()
    node_collection = object()

    monkeypatch.setattr("topographer.plot._require_matplotlib", lambda: fake_pyplot)
    monkeypatch.setattr("topographer.plot.nx.draw_networkx_edges", lambda *args, **kwargs: None)
    monkeypatch.setattr("topographer.plot.nx.draw_networkx_nodes", lambda *args, **kwargs: node_collection)
    monkeypatch.setattr("topographer.plot.nx.draw_networkx_labels", lambda *args, **kwargs: None)

    output_path = save_graph_plot(graph, tmp_path / "graph.png", scalar="height", title="Graph")

    assert output_path.exists()
    assert fake_pyplot.axis.axis_off is True
    assert fake_pyplot.figure.colorbar_calls == [
        {"mappable": node_collection, "ax": fake_pyplot.axis, "label": "height"}
    ]


def test_save_plot_helpers_write_files(tmp_path: Path) -> None:
    graph = make_graph()
    contour_tree = compute_contour_tree(graph, "height")
    branching_tree = make_branching_tree()
    pairs = compute_persistence(contour_tree, scalar="height")

    graph_path = save_graph_plot(graph, tmp_path / "graph.png", scalar="height", title="Graph")
    tree_path = save_tree_plot(branching_tree, tmp_path / "tree.png", title="Tree")
    diagram_path = save_persistence_diagram(
        pairs,
        tmp_path / "diagram.png",
        graph=graph,
        scalar="height",
        title="Diagram",
    )
    html_path = write_gallery_html(
        [{"title": "Graph", "filename": "graph.png"}],
        tmp_path / "index.html",
    )

    assert graph_path.exists()
    assert tree_path.exists()
    assert diagram_path.exists()
    assert html_path.exists()
