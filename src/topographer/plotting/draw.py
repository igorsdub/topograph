from __future__ import annotations

from collections.abc import Mapping
from importlib import import_module
from typing import Any, cast

import networkx as nx

from .layout import get_nx_tree, planar_layout
from .styles import CONTOUR_STYLE


def draw_edges(
    tree: Any,
    pos: Mapping[Any, tuple[float, float]],
    *,
    ax: Any,
    style: Mapping[str, Any] = CONTOUR_STYLE,
) -> None:
    """Draw tree edges using the provided positions."""
    graph = get_nx_tree(tree)
    edge_style = style["edges"]
    draw_networkx_edges = cast(Any, nx.draw_networkx_edges)
    draw_networkx_edges(
        graph,
        pos,
        ax=ax,
        width=edge_style["width"],
        edge_color=edge_style["edge_color"],
        alpha=edge_style["alpha"],
    )


def draw_nodes(
    tree: Any,
    pos: Mapping[Any, tuple[float, float]],
    *,
    ax: Any,
    node_size: float = 40.0,
    scalar_attr: str = "scalar",
    show_regular: bool = False,
    style: Mapping[str, Any] = CONTOUR_STYLE,
) -> None:
    """Draw tree nodes with topology-aware marker styling."""
    graph = get_nx_tree(tree)

    critical_groups = _classify_nodes(tree, scalar_attr=scalar_attr)

    regular_nodes = critical_groups["regular"]
    if not show_regular:
        regular_nodes = []

    draw_order = [
        ("regular", regular_nodes),
        ("saddles", critical_groups["saddles"]),
        ("minima", critical_groups["minima"]),
        ("maxima", critical_groups["maxima"]),
    ]

    for group_name, nodes in draw_order:
        if not nodes:
            continue

        group_style = style[group_name]
        z_order_map = {
            "regular": 1,
            "saddles": 2,
            "minima": 3,
            "maxima": 3,
        }
        draw_networkx_nodes = cast(Any, nx.draw_networkx_nodes)
        collection = draw_networkx_nodes(
            graph,
            pos,
            nodelist=nodes,
            ax=ax,
            node_shape=group_style["marker"],
            node_color=group_style["node_color"],
            node_size=max(float(group_style["node_size"]), float(node_size)),
            alpha=float(group_style.get("alpha", 1.0)),
            linewidths=0.6,
            edgecolors="#111111",
        )
        if collection is not None and hasattr(collection, "set_zorder"):
            collection.set_zorder(float(z_order_map[group_name]))


def annotate_nodes(
    tree: Any,
    pos: Mapping[Any, tuple[float, float]],
    *,
    ax: Any,
    label_attr: str | None = None,
    style: Mapping[str, Any] = CONTOUR_STYLE,
) -> None:
    """Add text labels to nodes."""
    graph = get_nx_tree(tree)
    labels_style = style["labels"]

    if label_attr is None:
        labels = {node: str(node) for node in graph.nodes}
    else:
        labels = {node: str(graph.nodes[node].get(label_attr, node)) for node in graph.nodes}

    draw_networkx_labels = cast(Any, nx.draw_networkx_labels)
    draw_networkx_labels(
        graph,
        pos,
        labels=labels,
        ax=ax,
        font_size=labels_style["font_size"],
        font_color=labels_style["font_color"],
    )


def draw_tree(
    tree: Any,
    pos: Mapping[Any, tuple[float, float]] | None = None,
    *,
    ax: Any | None = None,
    with_labels: bool = False,
    node_size: float = 40.0,
    show_regular: bool = False,
    scalar_attr: str = "scalar",
    label_attr: str | None = None,
    show_scalar_axis: bool = False,
    style: Mapping[str, Any] = CONTOUR_STYLE,
) -> tuple[Any, Any]:
    """Draw a tree with planar contour-style defaults."""
    try:
        plt = import_module("matplotlib.pyplot")
    except Exception as exc:
        raise RuntimeError("matplotlib is required for tree plotting") from exc

    graph = get_nx_tree(tree)
    resolved_pos = dict(pos) if pos is not None else planar_layout(graph, scalar=scalar_attr)

    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 5), constrained_layout=True)
    else:
        fig = ax.figure

    if ax is None:
        raise RuntimeError("Failed to create matplotlib axes")

    draw_edges(graph, resolved_pos, ax=ax, style=style)
    draw_nodes(
        graph,
        resolved_pos,
        ax=ax,
        node_size=node_size,
        scalar_attr=scalar_attr,
        show_regular=show_regular,
        style=style,
    )

    if with_labels:
        annotate_nodes(graph, resolved_pos, ax=ax, label_attr=label_attr, style=style)

    if show_scalar_axis:
        y_values = [coord[1] for coord in resolved_pos.values()]
        if y_values:
            y_min = min(y_values)
            y_max = max(y_values)
            if y_min == y_max:
                y_min -= 0.5
                y_max += 0.5
            padding = max((y_max - y_min) * 0.05, 1e-6)
            ax.set_ylim(y_min - padding, y_max + padding)

        ax.get_xaxis().set_visible(False)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["bottom"].set_visible(False)
        ax.set_ylabel(f"{scalar_attr} value")
    else:
        ax.set_axis_off()

    ax.set_title("Tree plot")
    return fig, ax


def plot_tree(
    tree: Any,
    *,
    scalar_attr: str = "scalar",
    ax: Any | None = None,
    with_labels: bool = False,
    show_regular: bool = False,
    show_scalar_axis: bool = False,
) -> tuple[Any, Any]:
    """Convenience wrapper: compute planar layout and draw the tree."""
    pos = planar_layout(tree, scalar=scalar_attr)
    return draw_tree(
        tree,
        pos=pos,
        ax=ax,
        with_labels=with_labels,
        show_regular=show_regular,
        scalar_attr=scalar_attr,
        show_scalar_axis=show_scalar_axis,
    )


def _classify_nodes(tree: Any, *, scalar_attr: str) -> dict[str, list[Any]]:
    graph = get_nx_tree(tree)
    critical_nodes = set(getattr(tree, "critical_nodes", []))

    minima: list[Any] = []
    maxima: list[Any] = []
    saddles: list[Any] = []
    regular: list[Any] = []

    for node in graph.nodes:
        kind = _node_kind(graph, node, scalar_attr=scalar_attr)
        if node not in critical_nodes and critical_nodes:
            kind = "regular"

        if kind == "minima":
            minima.append(node)
        elif kind == "maxima":
            maxima.append(node)
        elif kind == "saddles":
            saddles.append(node)
        else:
            regular.append(node)

    return {
        "minima": minima,
        "maxima": maxima,
        "saddles": saddles,
        "regular": regular,
    }


def _node_kind(graph: nx.Graph[Any], node: Any, *, scalar_attr: str) -> str:
    neighbors = list(graph.neighbors(node))
    if not neighbors:
        return "regular"

    node_scalar = float(graph.nodes[node][scalar_attr])
    greater = 0
    lower = 0

    for neighbor in neighbors:
        neighbor_scalar = float(graph.nodes[neighbor][scalar_attr])
        if neighbor_scalar > node_scalar:
            greater += 1
        elif neighbor_scalar < node_scalar:
            lower += 1

    if lower == 0 and greater > 0:
        return "minima"
    if greater == 0 and lower > 0:
        return "maxima"
    if greater > 0 and lower > 0:
        return "saddles"
    return "regular"


__all__ = [
    "draw_tree",
    "draw_nodes",
    "draw_edges",
    "annotate_nodes",
    "plot_tree",
]
