"""Topographer: minimal topology tools for graphs."""

from .api import run_pipeline
from .core import (
    UnionFind,
    check_graph,
    ensure_total_order,
    has_unique_scalars,
    make_total_ordering,
)
from .models import ContourTree, MergeTree, PersistencePair, PipelineResult
from .persistence import compute_persistence, compute_persistence_pairs
from .plot import (
    plot_graph,
    plot_persistence_diagram,
    plot_tree,
    scalar_layout,
    tree_plot_data,
)
from .simplify import simplify_contour_tree, simplify_tree_by_persistence
from .trees import (
    compute_contour_tree,
    compute_contour_tree_from_trees,
    compute_join_tree,
    compute_split_tree,
)

__all__ = [
    "ContourTree",
    "MergeTree",
    "PersistencePair",
    "PipelineResult",
    "UnionFind",
    "check_graph",
    "compute_contour_tree",
    "compute_contour_tree_from_trees",
    "compute_join_tree",
    "compute_persistence",
    "compute_persistence_pairs",
    "compute_split_tree",
    "ensure_total_order",
    "has_unique_scalars",
    "make_total_ordering",
    "plot_graph",
    "plot_persistence_diagram",
    "plot_tree",
    "run_pipeline",
    "scalar_layout",
    "simplify_contour_tree",
    "simplify_tree_by_persistence",
    "tree_plot_data",
]
