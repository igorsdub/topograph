"""Public pipeline API for the topographer package."""

from __future__ import annotations

import networkx as nx

from topographer.core import check_graph, ensure_total_order
from topographer.models import PipelineResult
from topographer.persistence import compute_persistence_pairs
from topographer.simplify import simplify_contour_tree
from topographer.trees import compute_contour_tree, compute_join_tree, compute_split_tree


def run_pipeline(
    G: nx.Graph,
    scalar: str,
    simplify_threshold: float | None = None,
) -> PipelineResult:
    """Run the full topological pipeline on a scalar graph.

    Parameters
    ----------
    G:
        Input graph with scalar values stored as node attributes.
    scalar:
        Name of the node attribute containing the scalar field.
    simplify_threshold:
        If provided, remove low-persistence contour-tree arcs below this threshold.

    Returns
    -------
    PipelineResult
        Dataclass containing the ordered graph and all intermediate outputs.
    """

    check_graph(G, scalar)
    ordered_graph, ordered_scalar = ensure_total_order(G, scalar)

    join_tree = compute_join_tree(ordered_graph, scalar)
    split_tree = compute_split_tree(ordered_graph, scalar)
    contour_tree = compute_contour_tree(split_tree, join_tree)
    persistence_pairs = compute_persistence_pairs(contour_tree)

    simplified_tree = None
    if simplify_threshold is not None:
        simplified_tree = simplify_contour_tree(
            contour_tree,
            persistence_pairs,
            threshold=simplify_threshold,
        )

    return PipelineResult(
        input_graph=G,
        ordered_graph=ordered_graph,
        scalar=scalar,
        ordered_scalar=ordered_scalar,
        join_tree=join_tree,
        split_tree=split_tree,
        contour_tree=contour_tree,
        persistence_pairs=persistence_pairs,
        simplified_contour_tree=simplified_tree,
    )
