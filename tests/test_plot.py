"""Tests for lightweight plotting data helpers."""

from __future__ import annotations

from pathlib import Path

import networkx as nx

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


def test_plot_graph_returns_positions_edges_and_nodes() -> None:
    graph = make_graph()

    data = plot_graph(graph, scalar="height")

    assert set(data) == {"positions", "edges", "nodes"}
    assert set(data["nodes"]) == set(graph.nodes)
    assert len(data["positions"]) == graph.number_of_nodes()


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


def test_save_graph_plot_uses_only_scalar_y_axis(monkeypatch, tmp_path: Path) -> None:
    graph = make_graph()

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
            self.ylabel = ""
            self.grid_called = False
            self.margins_value = None
            self.tick_params_calls: list[dict[str, object]] = []
            self.xaxis = FakeAxisVisibility()
            self.yaxis = FakeAxisVisibility()
            self.spines = {
                "top": FakeSpine(),
                "right": FakeSpine(),
                "bottom": FakeSpine(),
                "left": FakeSpine(),
            }

        def set_title(self, title: str) -> None:
            self.title = title

        def set_ylabel(self, label: str) -> None:
            self.ylabel = label

        def get_xaxis(self) -> FakeAxisVisibility:
            return self.xaxis

        def get_yaxis(self) -> FakeAxisVisibility:
            return self.yaxis

        def tick_params(self, **kwargs: object) -> None:
            self.tick_params_calls.append(kwargs)

        def margins(self, value: float) -> None:
            self.margins_value = value

        def grid(self, *args: object, **kwargs: object) -> None:
            self.grid_called = True

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

    fake_pyplot = FakePyplot()

    monkeypatch.setattr("topographer.plot._require_matplotlib", lambda: fake_pyplot)
    monkeypatch.setattr("topographer.plot.nx.draw_networkx_edges", lambda *args, **kwargs: None)
    monkeypatch.setattr("topographer.plot.nx.draw_networkx_nodes", lambda *args, **kwargs: None)
    monkeypatch.setattr("topographer.plot.nx.draw_networkx_labels", lambda *args, **kwargs: None)

    output_path = save_graph_plot(graph, tmp_path / "graph.png", scalar="height", title="Graph")

    assert output_path.exists()
    assert fake_pyplot.axis.ylabel == "height"
    assert fake_pyplot.axis.grid_called is False
    assert fake_pyplot.axis.xaxis.visible is False
    assert fake_pyplot.axis.yaxis.visible is True
    assert fake_pyplot.axis.spines["bottom"].visible is False
    assert fake_pyplot.axis.tick_params_calls == [
        {"axis": "x", "which": "both", "bottom": False, "labelbottom": False}
    ]


def test_save_plot_helpers_write_files(tmp_path: Path) -> None:
    graph = make_graph()
    contour_tree = compute_contour_tree(graph, "height")
    pairs = compute_persistence(contour_tree, scalar="height")

    graph_path = save_graph_plot(graph, tmp_path / "graph.png", scalar="height", title="Graph")
    tree_path = save_tree_plot(contour_tree, tmp_path / "tree.png", title="Tree")
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
