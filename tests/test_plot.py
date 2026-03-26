"""Tests for lightweight plotting data helpers."""

from __future__ import annotations

from pathlib import Path

import networkx as nx

from topographer.examples import make_cave_man_graph
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
from topographer.trees import compute_contour_tree, compute_join_tree


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


def make_typed_tree() -> MergeTree:
    """Create a tree that covers each supported tree marker type."""

    graph = nx.Graph()
    graph.add_edges_from(
        [
            ("min", "join"),
            ("join", "max"),
            ("join", "reg"),
            ("reg", "split"),
            ("split", "fallback"),
        ]
    )
    nx.set_node_attributes(
        graph,
        {
            "min": 0.0,
            "join": 1.0,
            "reg": 2.0,
            "split": 3.0,
            "fallback": 4.0,
            "max": 5.0,
        },
        "height",
    )
    graph.nodes["min"]["node_type"] = "min"
    graph.nodes["min"]["saddle_type"] = None
    graph.nodes["join"]["node_type"] = "sad"
    graph.nodes["join"]["saddle_type"] = "join_sad"
    graph.nodes["reg"]["node_type"] = "reg"
    graph.nodes["reg"]["saddle_type"] = None
    graph.nodes["split"]["node_type"] = "sad"
    graph.nodes["split"]["saddle_type"] = "split_sad"
    graph.nodes["max"]["node_type"] = "max"
    graph.nodes["max"]["saddle_type"] = None
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
    assert set(data) == {"positions", "edges", "nodes", "markers", "marker_groups"}


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


def test_plot_tree_returns_markers_from_node_types() -> None:
    tree = make_typed_tree()

    data = plot_tree(tree)

    assert data["markers"] == {
        "min": "v",
        "join": "D",
        "reg": "o",
        "split": "v",
        "fallback": "o",
        "max": "^",
    }
    assert data["marker_groups"] == {
        "v": ["min", "split"],
        "D": ["join"],
        "^": ["max"],
        "o": ["reg", "fallback"],
    }


def test_plot_tree_marks_cave_man_join_saddle_with_diamond() -> None:
    graph = make_cave_man_graph()

    join_tree = compute_join_tree(graph)
    plot_data = plot_tree(join_tree)

    assert (
        join_tree.graph.nodes[2]["node_type"],
        join_tree.graph.nodes[2]["saddle_type"],
    ) == ("sad", "join_sad")
    assert (
        join_tree.graph.nodes[5]["node_type"],
        join_tree.graph.nodes[5]["saddle_type"],
    ) == ("max", None)
    assert plot_data["markers"][2] == "D"
    assert plot_data["markers"][5] == "^"


def test_plot_tree_marks_explicit_global_endpoints_in_merge_trees() -> None:
    graph = nx.path_graph(4)
    nx.set_node_attributes(graph, {0: 0.0, 1: 1.0, 2: 2.0, 3: 3.0}, "height")

    join_tree = compute_contour_tree(graph, "height").join_tree
    split_tree = compute_contour_tree(graph, "height").split_tree

    assert join_tree is not None
    assert split_tree is not None
    assert plot_tree(join_tree)["markers"][3] == "^"
    assert plot_tree(split_tree)["markers"][0] == "v"


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


def test_save_tree_plot_draws_node_groups_by_marker(monkeypatch, tmp_path: Path) -> None:
    tree = make_typed_tree()

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
            self.xaxis = FakeAxisVisibility()
            self.yaxis = FakeAxisVisibility()
            self.tick_calls: list[dict[str, object]] = []
            self.spines = {name: FakeSpine() for name in ("top", "right", "bottom")}
            self.margins_value = None

        def set_title(self, title: str) -> None:
            self.title = title

        def set_ylabel(self, value: str) -> None:
            self.ylabel = value

        def get_xaxis(self) -> FakeAxisVisibility:
            return self.xaxis

        def get_yaxis(self) -> FakeAxisVisibility:
            return self.yaxis

        def tick_params(self, **kwargs: object) -> None:
            self.tick_calls.append(kwargs)

        def margins(self, value: float) -> None:
            self.margins_value = value

    class FakeFigure:
        def __init__(self) -> None:
            self.tight_layout_called = False
            self.saved_paths: list[Path] = []

        def tight_layout(self) -> None:
            self.tight_layout_called = True

        def savefig(self, path: Path, dpi: int) -> None:
            self.saved_paths.append(path)
            path.write_text("fake image", encoding="utf-8")

    class FakePyplot:
        def __init__(self) -> None:
            self.figure = FakeFigure()
            self.axis = FakeAxis()
            self.closed_figures: list[FakeFigure] = []

        def subplots(self, figsize: tuple[float, float]) -> tuple[FakeFigure, FakeAxis]:
            return self.figure, self.axis

        def close(self, figure: FakeFigure) -> None:
            self.closed_figures.append(figure)

    draw_calls: list[dict[str, object]] = []
    fake_pyplot = FakePyplot()

    monkeypatch.setattr("topographer.plot._require_matplotlib", lambda: fake_pyplot)
    monkeypatch.setattr("topographer.plot.nx.draw_networkx_edges", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        "topographer.plot.nx.draw_networkx_nodes",
        lambda *args, **kwargs: draw_calls.append(kwargs),
    )
    monkeypatch.setattr("topographer.plot.nx.draw_networkx_labels", lambda *args, **kwargs: None)

    output_path = save_tree_plot(tree, tmp_path / "tree.png", title="Tree")

    assert output_path.exists()
    assert draw_calls == [
        {
            "pos": plot_tree(tree)["positions"],
            "nodelist": ["min", "split"],
            "ax": fake_pyplot.axis,
            "node_color": "#2b5d73",
            "node_size": 900,
            "edgecolors": "#172033",
            "linewidths": 1.2,
            "node_shape": "v",
        },
        {
            "pos": plot_tree(tree)["positions"],
            "nodelist": ["join"],
            "ax": fake_pyplot.axis,
            "node_color": "#2b5d73",
            "node_size": 760,
            "edgecolors": "#172033",
            "linewidths": 1.2,
            "node_shape": "D",
        },
        {
            "pos": plot_tree(tree)["positions"],
            "nodelist": ["max"],
            "ax": fake_pyplot.axis,
            "node_color": "#2b5d73",
            "node_size": 900,
            "edgecolors": "#172033",
            "linewidths": 1.2,
            "node_shape": "^",
        },
        {
            "pos": plot_tree(tree)["positions"],
            "nodelist": ["reg", "fallback"],
            "ax": fake_pyplot.axis,
            "node_color": "#2b5d73",
            "node_size": 900,
            "edgecolors": "#172033",
            "linewidths": 1.2,
            "node_shape": "o",
        },
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
