from __future__ import annotations

from pathlib import Path

import networkx as nx
import pytest

from topographer.models.tree import MergeTree
from topographer.plotting import draw_tree, planar_layout, save_figure
from topographer.plotting.styles import CONTOUR_STYLE


def _tree_graph() -> nx.Graph[str]:
    graph: nx.Graph[str] = nx.Graph()
    graph.add_node("r", scalar=10.0)
    graph.add_node("a", scalar=6.0)
    graph.add_node("b", scalar=5.0)
    graph.add_node("c", scalar=1.0)
    graph.add_node("d", scalar=2.0)
    graph.add_edges_from(
        [
            ("r", "a"),
            ("r", "b"),
            ("a", "c"),
            ("a", "d"),
        ]
    )
    return graph


def test_planar_layout_accepts_merge_tree_wrapper() -> None:
    graph = _tree_graph()
    wrapper = MergeTree(
        graph=graph,
        root="r",
        critical_nodes=["r", "a", "b", "c", "d"],
        scalar="scalar",
        kind="join",
    )

    pos = planar_layout(wrapper)

    assert set(pos) == set(graph.nodes)


def test_draw_tree_and_save_supported_formats(tmp_path: Path) -> None:
    matplotlib = pytest.importorskip("matplotlib")
    matplotlib.use("Agg")
    pytest.importorskip("matplotlib.pyplot")

    graph = _tree_graph()
    pos = planar_layout(graph)
    fig, _ = draw_tree(graph, pos=pos, with_labels=True)

    png_path = tmp_path / "tree_plot.png"
    svg_path = tmp_path / "tree_plot.svg"
    html_path = tmp_path / "tree_plot.html"

    save_figure(fig, png_path)
    save_figure(fig, svg_path)
    save_figure(fig, html_path)

    assert png_path.exists()
    assert svg_path.exists()
    assert html_path.exists()
    html_text = html_path.read_text(encoding="utf-8")
    assert "<svg" in html_text


def test_save_figure_rejects_unknown_format(tmp_path: Path) -> None:
    matplotlib = pytest.importorskip("matplotlib")
    matplotlib.use("Agg")
    pytest.importorskip("matplotlib.pyplot")

    graph = _tree_graph()
    fig, _ = draw_tree(graph)

    with pytest.raises(ValueError, match="Unsupported figure format"):
        save_figure(fig, tmp_path / "tree_plot.bmp")


def test_draw_tree_can_show_scalar_side_axis() -> None:
    matplotlib = pytest.importorskip("matplotlib")
    matplotlib.use("Agg")
    pytest.importorskip("matplotlib.pyplot")

    graph = _tree_graph()
    fig, ax = draw_tree(graph, show_scalar_axis=True, scalar_attr="scalar")

    assert ax.get_ylabel() == "scalar value"
    assert ax.xaxis.get_visible() is False
    assert fig is not None


def test_critical_marker_shapes_match_spec() -> None:
    assert CONTOUR_STYLE["minima"]["marker"] == "o"
    assert CONTOUR_STYLE["maxima"]["marker"] == "^"
    assert CONTOUR_STYLE["saddles"]["marker"] == "D"
