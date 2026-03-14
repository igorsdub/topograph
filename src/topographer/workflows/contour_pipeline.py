from __future__ import annotations

"""High-level contour-tree workflow orchestration."""

from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from typing import Any

import networkx as nx

from topographer.algorithms.contour_tree import compute_contour_tree_from_split_join
from topographer.algorithms.join_tree import compute_join_tree
from topographer.algorithms.persistence import (
    compute_persistence_from_contour_tree,
    compute_persistence_from_split_join,
)
from topographer.algorithms.simplification import simplify_contour_tree
from topographer.algorithms.split_tree import compute_split_tree
from topographer.core.graph_check import check_graph
from topographer.models.persistence import PersistenceResult
from topographer.models.tree import ContourTree, MergeTree
from topographer.plotting import draw_tree, plot_persistence_diagram, plot_tree, save_figure
from topographer.transforms.perturb import PerturbationResult, perturb_ties


@dataclass(slots=True)
class ContourPipelineArtifacts:
    """Artifacts emitted by the full contour workflow."""

    raw_graph: nx.Graph
    graph: nx.Graph
    scalar: str
    perturbation: PerturbationResult | None
    split_tree: MergeTree
    join_tree: MergeTree
    contour_tree: ContourTree
    persistence: PersistenceResult
    simplified_contour_tree: ContourTree
    simplified_persistence: PersistenceResult


def medium_example_graph() -> nx.Graph:
    """Build a medium-complexity connected graph with tied scalar values."""
    graph = nx.Graph()
    graph.add_edges_from(
        [
            (0, 1),
            (1, 2),
            (2, 3),
            (2, 4),
            (4, 5),
            (1, 6),
            (6, 7),
            (6, 8),
            (8, 9),
            (4, 10),
            (10, 11),
        ]
    )

    scalars = {
        0: 9.0,
        1: 7.5,
        2: 6.0,
        3: 2.0,
        4: 4.0,
        5: 2.0,
        6: 5.5,
        7: 1.0,
        8: 3.5,
        9: 1.0,
        10: 4.5,
        11: 0.0,
    }
    nx.set_node_attributes(graph, scalars, "scalar")
    return graph


def run_contour_pipeline(
    graph: nx.Graph,
    *,
    scalar: str = "scalar",
    simplification_threshold: float = 1.5,
    break_scalar_ties: bool = True,
    require_connected: bool = True,
) -> ContourPipelineArtifacts:
    """Run full workflow: checks, uniqueness, ST/JT, CT, persistence, simplification."""
    raw_graph = graph.copy()
    working_graph = graph.copy()

    perturbation: PerturbationResult | None = None
    try:
        check_graph(working_graph, scalar_attr=scalar, require_connected=require_connected)
    except ValueError as exc:
        if "Duplicate scalar values detected" not in str(exc) or not break_scalar_ties:
            raise

        perturbation = perturb_ties(
            working_graph,
            scalar=scalar,
            output_scalar=scalar,
            inplace=True,
        )
        check_graph(working_graph, scalar_attr=scalar, require_connected=require_connected)

    split_tree = compute_split_tree(
        working_graph,
        scalar=scalar,
        require_connected=require_connected,
    )
    join_tree = compute_join_tree(
        working_graph,
        scalar=scalar,
        require_connected=require_connected,
    )
    contour_tree = compute_contour_tree_from_split_join(split_tree, join_tree)

    persistence = compute_persistence_from_split_join(split_tree, join_tree)

    simplified_contour_tree = simplify_contour_tree(
        contour_tree,
        threshold=simplification_threshold,
    )
    simplified_persistence = compute_persistence_from_contour_tree(simplified_contour_tree)

    return ContourPipelineArtifacts(
        raw_graph=raw_graph,
        graph=working_graph,
        scalar=scalar,
        perturbation=perturbation,
        split_tree=split_tree,
        join_tree=join_tree,
        contour_tree=contour_tree,
        persistence=persistence,
        simplified_contour_tree=simplified_contour_tree,
        simplified_persistence=simplified_persistence,
    )


def run_medium_example_pipeline(
    *,
    simplification_threshold: float = 1.5,
) -> ContourPipelineArtifacts:
    """Run the full pipeline on a medium built-in example graph."""
    return run_contour_pipeline(
        medium_example_graph(),
        simplification_threshold=simplification_threshold,
    )


def create_pipeline_figures(
    artifacts: ContourPipelineArtifacts,
    *,
    with_labels: bool = False,
    show_regular: bool = False,
) -> dict[str, Any]:
    """Create matplotlib figures for trees and persistence diagrams."""
    _hydrate_scalar_attributes(artifacts.split_tree, scalar=artifacts.scalar)
    _hydrate_scalar_attributes(artifacts.join_tree, scalar=artifacts.scalar)
    _hydrate_scalar_attributes(artifacts.contour_tree, scalar=artifacts.scalar)
    _hydrate_scalar_attributes(artifacts.simplified_contour_tree, scalar=artifacts.scalar)

    figures: dict[str, Any] = {}

    fig_g, _ = _plot_original_graph(artifacts.raw_graph, scalar=artifacts.scalar)
    figures["original_graph"] = fig_g

    fig_st, ax_st = _plot_topology(
        artifacts.split_tree,
        scalar=artifacts.scalar,
        with_labels=with_labels,
        show_regular=show_regular,
    )
    ax_st.set_title("Split Tree")
    figures["split_tree"] = fig_st

    fig_jt, ax_jt = _plot_topology(
        artifacts.join_tree,
        scalar=artifacts.scalar,
        with_labels=with_labels,
        show_regular=show_regular,
    )
    ax_jt.set_title("Join Tree")
    figures["join_tree"] = fig_jt

    fig_ct, ax_ct = _plot_topology(
        artifacts.contour_tree,
        scalar=artifacts.scalar,
        with_labels=with_labels,
        show_regular=show_regular,
    )
    ax_ct.set_title("Contour Tree")
    figures["contour_tree"] = fig_ct

    fig_ct_s, ax_ct_s = _plot_topology(
        artifacts.simplified_contour_tree,
        scalar=artifacts.scalar,
        with_labels=with_labels,
        show_regular=show_regular,
    )
    ax_ct_s.set_title("Simplified Contour Tree")
    figures["contour_tree_simplified"] = fig_ct_s

    fig_pd, _ = plot_persistence_diagram(
        artifacts.persistence,
        title="Persistence Diagram",
    )
    figures["persistence_diagram"] = fig_pd

    fig_pd_s, _ = plot_persistence_diagram(
        artifacts.simplified_persistence,
        title="Persistence Diagram (Simplified)",
    )
    figures["persistence_diagram_simplified"] = fig_pd_s

    return figures


def _hydrate_scalar_attributes(tree: MergeTree | ContourTree, *, scalar: str) -> None:
    """Write scalar metadata to graph nodes for plotting/layout helpers."""
    for node in tree.graph.nodes:
        metadata = tree.node_metadata.get(node)
        if metadata is None or scalar not in metadata:
            continue
        tree.graph.nodes[node][scalar] = float(metadata[scalar])


def _plot_topology(
    tree: MergeTree | ContourTree,
    *,
    scalar: str,
    with_labels: bool,
    show_regular: bool,
) -> tuple[Any, Any]:
    """Plot as planar tree when possible; otherwise use a spring-layout fallback."""
    if nx.is_tree(tree.graph):
        return plot_tree(
            tree,
            scalar_attr=scalar,
            with_labels=with_labels,
            show_regular=show_regular,
            show_scalar_axis=True,
        )

    pos_raw = nx.spring_layout(tree.graph, seed=7)
    pos = {
        node: (
            float(coord[0]),
            float(tree.graph.nodes[node].get(scalar, coord[1])),
        )
        for node, coord in pos_raw.items()
    }
    return draw_tree(
        tree,
        pos=pos,
        with_labels=with_labels,
        show_regular=show_regular,
        scalar_attr=scalar,
        show_scalar_axis=True,
    )


def _plot_original_graph(graph: nx.Graph, *, scalar: str) -> tuple[Any, Any]:
    """Plot the original graph with node colors mapped to scalar values."""
    try:
        plt = import_module("matplotlib.pyplot")
    except Exception as exc:
        raise RuntimeError("matplotlib is required for graph plotting") from exc

    fig, ax = plt.subplots(figsize=(7, 5), constrained_layout=True)
    pos = nx.spring_layout(graph, seed=7)

    values = [float(graph.nodes[node][scalar]) for node in graph.nodes]

    nx.draw_networkx_edges(graph, pos, ax=ax, width=1.2, alpha=0.8, edge_color="#4c4c4c")
    node_collection = nx.draw_networkx_nodes(
        graph,
        pos,
        ax=ax,
        node_color=values,
        cmap="viridis",
        node_size=120,
        linewidths=0.6,
        edgecolors="#111111",
    )
    nx.draw_networkx_labels(graph, pos, ax=ax, font_size=8)

    colorbar = fig.colorbar(node_collection, ax=ax)
    colorbar.set_label(f"{scalar} value")
    ax.set_title("Original Graph")
    ax.set_axis_off()
    return fig, ax


def save_pipeline_figures(
    figures: dict[str, Any],
    output_dir: str | Path,
    *,
    format: str = "svg",
) -> dict[str, Path]:
    """Save pipeline figures to ``output_dir`` and return output paths."""
    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    outputs: dict[str, Path] = {}
    for name, figure in figures.items():
        output_path = target_dir / f"{name}.{format}"
        outputs[name] = save_figure(figure, output_path, format=format)
    return outputs


__all__ = [
    "ContourPipelineArtifacts",
    "medium_example_graph",
    "run_contour_pipeline",
    "run_medium_example_pipeline",
    "create_pipeline_figures",
    "save_pipeline_figures",
]
