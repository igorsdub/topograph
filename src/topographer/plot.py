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
    """Place nodes by index on x and scalar value on y."""

    ordered_nodes = sorted(G.nodes, key=lambda node: (float(G.nodes[node][scalar]), str(node)))
    return {
        node: (float(index), float(G.nodes[node][scalar]))
        for index, node in enumerate(ordered_nodes)
    }


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

    return tree_plot_data(G, scalar)


def plot_tree(tree: MergeTree | ContourTree) -> dict[str, object]:
    """Return lightweight plotting data for a merge or contour tree."""

    return tree_plot_data(tree.graph, tree.scalar)


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
    """Render a graph or tree to an image file."""

    plt = _require_matplotlib()
    data = plot_graph(graph, scalar=scalar)
    positions = data["positions"]
    labels = {node: f"{node}\n{float(graph.nodes[node][scalar]):.1f}" for node in graph.nodes}

    figure, axis = plt.subplots(figsize=(8, 4.8))
    if title:
        axis.set_title(title)
    axis.set_xlabel("Scalar Order")
    axis.set_ylabel("Scalar Value")
    axis.set_facecolor("#fffdf8")
    axis.grid(color="#ddd4c7", linewidth=0.8, alpha=0.8)

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


def save_tree_plot(
    tree: MergeTree | ContourTree,
    path: str | Path,
    *,
    title: str = "",
    node_color: str = "#2b5d73",
    edge_color: str = "#516170",
) -> Path:
    """Render a merge tree or contour tree to an image file."""

    return save_graph_plot(
        tree.graph,
        path,
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
    <p>This gallery was generated by <code>examples/basic_pipeline.py</code>.</p>
{sections}
  </main>
</body>
</html>
"""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    return output_path

