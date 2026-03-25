"""Minimal plotting helpers for graphs, trees, and persistence pairs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import networkx as nx

from .models import ContourTree, MergeTree, PersistencePair


def scalar_layout(
    G: nx.Graph,
    scalar: str = "scalar",
) -> dict[object, tuple[float, float]]:
    """Place nodes using only the scalar value on the y-axis."""

    return {
        node: (0.0, float(G.nodes[node][scalar]))
        for node in G.nodes
    }


def _graph_layout(G: nx.Graph) -> dict[object, tuple[float, float]]:
    """Return a deterministic layout for a plain graph plot."""

    if all("pos" in G.nodes[node] for node in G.nodes):
        return {
            node: (float(G.nodes[node]["pos"][0]), float(G.nodes[node]["pos"][1]))
            for node in G.nodes
        }

    positions = nx.spring_layout(G, seed=0)
    return {
        node: (float(position[0]), float(position[1]))
        for node, position in positions.items()
    }


def _node_order_key(G: nx.Graph, node: object, scalar: str) -> tuple[float, str]:
    """Return a stable ordering key based on scalar value and node identity."""

    return (float(G.nodes[node][scalar]), repr(node))


def _subtree_layout(
    G: nx.Graph,
    node: object,
    parent: object,
    scalar: str,
    blocked: set[object],
    next_leaf_x: float,
) -> tuple[dict[object, float], float]:
    """Assign relative x coordinates for a rooted subtree."""

    children = sorted(
        (
            neighbor
            for neighbor in G.neighbors(node)
            if neighbor != parent and neighbor not in blocked
        ),
        key=lambda child: _node_order_key(G, child, scalar),
    )
    if not children:
        return {node: next_leaf_x}, next_leaf_x + 1.0

    positions: dict[object, float] = {}
    child_x_values: list[float] = []
    current_leaf_x = next_leaf_x
    for child in children:
        child_positions, current_leaf_x = _subtree_layout(
            G,
            child,
            node,
            scalar,
            blocked,
            current_leaf_x,
        )
        positions.update(child_positions)
        child_x_values.append(child_positions[child])

    positions[node] = sum(child_x_values) / len(child_x_values)
    return positions, current_leaf_x


def _tree_scalar_layout(
    G: nx.Graph,
    scalar: str,
) -> dict[object, tuple[float, float]]:
    """Place a tree with scalar-driven y coordinates and planar branch spacing."""

    if not nx.is_tree(G):
        raise ValueError("Tree plotting requires a tree graph.")

    minimum = min(G.nodes, key=lambda node: _node_order_key(G, node, scalar))
    maximum = max(G.nodes, key=lambda node: _node_order_key(G, node, scalar))
    trunk = nx.shortest_path(G, source=minimum, target=maximum)
    trunk_set = set(trunk)

    positions = {
        node: (0.0, float(G.nodes[node][scalar]))
        for node in trunk
    }
    attachments = sorted(
        (
            (trunk_node, neighbor)
            for trunk_node in trunk
            for neighbor in G.neighbors(trunk_node)
            if neighbor not in trunk_set
        ),
        key=lambda item: (
            _node_order_key(G, item[0], scalar),
            _node_order_key(G, item[1], scalar),
        ),
    )

    side_offsets = {-1: 0.0, 1: 0.0}
    for index, (trunk_node, root) in enumerate(attachments):
        side = -1 if index % 2 == 0 else 1
        relative_x, next_leaf_x = _subtree_layout(
            G,
            root,
            trunk_node,
            scalar,
            trunk_set,
            next_leaf_x=0.0,
        )
        width = max(1.0, next_leaf_x)
        base_offset = side_offsets[side] + 1.0
        for node, x_value in relative_x.items():
            positions[node] = (
                side * (base_offset + x_value),
                float(G.nodes[node][scalar]),
            )
        side_offsets[side] += width + 1.0

    return positions


def tree_plot_data(
    G: nx.Graph,
    scalar: str = "scalar",
) -> dict[str, object]:
    """Return lightweight plotting data without depending on a graphics library."""

    return {
        "positions": scalar_layout(G, scalar),
        "edges": list(G.edges()),
        "nodes": list(G.nodes()),
    }


def plot_graph(G: nx.Graph, scalar: str = "scalar") -> dict[str, object]:
    """Return lightweight plotting data for an input graph."""

    return {
        "positions": _graph_layout(G),
        "edges": list(G.edges()),
        "nodes": list(G.nodes()),
    }


def plot_tree(tree: MergeTree | ContourTree) -> dict[str, object]:
    """Return lightweight plotting data for a merge or contour tree."""

    positions = (
        _tree_scalar_layout(tree.graph, tree.scalar)
        if nx.is_tree(tree.graph)
        else scalar_layout(tree.graph, tree.scalar)
    )
    return {
        "positions": positions,
        "edges": list(tree.graph.edges()),
        "nodes": list(tree.graph.nodes()),
    }


def plot_persistence_diagram(
    pairs: list[PersistencePair],
    graph: nx.Graph | None = None,
    scalar: str = "scalar",
) -> dict[str, object]:
    """Return point data for a persistence-diagram style plot."""

    if graph is None:
        points = [(pair.birth, pair.death, pair.persistence) for pair in pairs]
    else:
        points = [
            (
                float(graph.nodes[pair.birth][scalar]),
                float(graph.nodes[pair.death][scalar]),
                pair.persistence,
            )
            for pair in pairs
        ]
    return {"points": points}


def _require_matplotlib():
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ModuleNotFoundError as error:
        raise RuntimeError(
            "matplotlib is required for rendered plots. Install the project dependencies first."
        ) from error
    return plt


def save_graph_plot(
    graph: nx.Graph,
    path: str | Path,
    *,
    scalar: str = "scalar",
    title: str = "",
    node_color: str = "#2b5d73",
    edge_color: str = "#516170",
) -> Path:
    """Render a graph using its layout and scalar-based node coloring."""

    del node_color
    return _save_scalar_colored_graph_plot(
        graph,
        path,
        positions=plot_graph(graph, scalar=scalar)["positions"],
        scalar=scalar,
        title=title,
        edge_color=edge_color,
    )


def _save_network_plot(
    graph: nx.Graph,
    path: str | Path,
    *,
    positions: dict[object, tuple[float, float]],
    scalar: str,
    title: str,
    node_color: str,
    edge_color: str,
) -> Path:
    """Render a graph with precomputed node positions to an image file."""

    plt = _require_matplotlib()
    labels = {node: f"{node}\n{float(graph.nodes[node][scalar]):.1f}" for node in graph.nodes}

    figure, axis = plt.subplots(figsize=(8, 4.8))
    if title:
        axis.set_title(title)
    axis.set_ylabel(scalar)
    axis.get_xaxis().set_visible(False)
    axis.get_yaxis().set_visible(True)
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)
    axis.spines["bottom"].set_visible(False)
    axis.tick_params(axis="x", which="both", bottom=False, labelbottom=False)

    nx.draw_networkx_edges(graph, pos=positions, ax=axis, edge_color=edge_color, width=2.2)
    nx.draw_networkx_nodes(
        graph,
        pos=positions,
        ax=axis,
        node_color=node_color,
        node_size=900,
        edgecolors="#172033",
        linewidths=1.2,
    )
    nx.draw_networkx_labels(graph, pos=positions, labels=labels, ax=axis, font_size=9, font_color="white")

    axis.margins(0.18)
    figure.tight_layout()
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, dpi=180)
    plt.close(figure)
    return output_path


def _save_scalar_colored_graph_plot(
    graph: nx.Graph,
    path: str | Path,
    *,
    positions: dict[object, tuple[float, float]],
    scalar: str,
    title: str,
    edge_color: str,
) -> Path:
    """Render a graph using layout positions and scalar-based node coloring."""

    plt = _require_matplotlib()
    labels = {node: str(node) for node in graph.nodes}
    scalar_values = [float(graph.nodes[node][scalar]) for node in graph.nodes]

    figure, axis = plt.subplots(figsize=(8, 4.8))
    if title:
        axis.set_title(title)
    axis.set_axis_off()

    nx.draw_networkx_edges(graph, pos=positions, ax=axis, edge_color=edge_color, width=2.2)
    node_collection = nx.draw_networkx_nodes(
        graph,
        pos=positions,
        ax=axis,
        node_color=scalar_values,
        cmap=plt.cm.viridis,
        node_size=900,
        edgecolors="#172033",
        linewidths=1.2,
    )
    nx.draw_networkx_labels(graph, pos=positions, labels=labels, ax=axis, font_size=9, font_color="white")
    figure.colorbar(node_collection, ax=axis, label=scalar)

    axis.margins(0.18)
    figure.tight_layout()
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, dpi=180)
    plt.close(figure)
    return output_path


def save_tree_plot(
    tree: MergeTree | ContourTree,
    path: str | Path,
    *,
    title: str = "",
    node_color: str = "#2b5d73",
    edge_color: str = "#516170",
) -> Path:
    """Render a merge tree or contour tree to an image file."""

    return _save_network_plot(
        tree.graph,
        path,
        positions=plot_tree(tree)["positions"],
        scalar=tree.scalar,
        title=title,
        node_color=node_color,
        edge_color=edge_color,
    )


def save_persistence_diagram(
    pairs: list[PersistencePair],
    path: str | Path,
    *,
    graph: nx.Graph,
    scalar: str = "scalar",
    title: str = "",
    point_color: str = "#4b87a6",
) -> Path:
    """Render a persistence diagram to an image file."""

    plt = _require_matplotlib()
    data = plot_persistence_diagram(pairs, graph=graph, scalar=scalar)
    points = data["points"]

    figure, axis = plt.subplots(figsize=(5.4, 5.4))
    if title:
        axis.set_title(title)
    axis.set_xlabel("Birth Scalar")
    axis.set_ylabel("Death Scalar")
    axis.set_facecolor("#fffdf8")
    axis.grid(color="#ddd4c7", linewidth=0.8, alpha=0.8)

    if points:
        x_values = [point[0] for point in points]
        y_values = [point[1] for point in points]
        low = min(x_values + y_values)
        high = max(x_values + y_values)
        axis.plot([low, high], [low, high], linestyle="--", color="#8e877e", linewidth=1.2)
        axis.scatter(
            x_values,
            y_values,
            s=[240 + 70 * point[2] for point in points],
            color=point_color,
            edgecolors="#172033",
            linewidths=1.0,
            alpha=0.88,
        )
        axis.set_xlim(low - 0.2, high + 0.2)
        axis.set_ylim(low - 0.2, high + 0.2)
    else:
        axis.text(
            0.5,
            0.5,
            "No persistence pairs\nremain after simplification",
            ha="center",
            va="center",
            transform=axis.transAxes,
            color="#5a534b",
        )

    figure.tight_layout()
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, dpi=180)
    plt.close(figure)
    return output_path


def write_gallery_html(
    stages: list[dict[str, str]],
    path: str | Path,
    *,
    title: str = "Topographer Pipeline Example",
) -> Path:
    """Write a tiny HTML page listing the generated stage images."""

    sections = "\n".join(
        f"""    <section>
      <h2>{stage["title"]}</h2>
      <img src="{stage["filename"]}" alt="{stage["title"]}" />
    </section>"""
        for stage in stages
    )
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>{title}</title>
  <style>
    body {{ margin: 24px; background: #f8f6f1; color: #172033; font-family: monospace; }}
    main {{ max-width: 1040px; margin: 0 auto; }}
    section {{ margin-bottom: 28px; }}
    img {{ max-width: 100%; height: auto; border: 1px solid #d9d1c7; background: white; }}
    code {{ background: #ece8df; padding: 2px 4px; }}
  </style>
</head>
<body>
  <main>
    <h1>{title}</h1>
    <p>This gallery was generated by <code>examples/path_graph_pipeline.py</code>.</p>
{sections}
  </main>
</body>
</html>
"""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    return output_path
