"""Topographer: minimal topology tools for graphs."""

from .api import run_pipeline
from .core import (
    UnionFind,
    check_graph,
    ensure_total_order,
    has_unique_scalars,
    make_total_ordering,
)
from .examples import (
    make_balanced_tree_graph,
    make_cave_man_graph,
    make_circular_graph,
    make_cubical_graph,
    make_ladder_graph,
    make_path_graph,
    make_star_graph,
    make_tadpole_graph,
    make_trivial_graph,
    make_wheel_graph,
    make_windmill_graph,
)
from .models import ContourTree, MergeTree, PersistencePair, PipelineResult
from .persistence import compute_persistence, compute_persistence_pairs
from .plot import (
    plot_graph,
    plot_persistence_diagram,
    plot_tree,
    save_graph_plot,
    save_persistence_diagram,
    save_tree_plot,
    scalar_layout,
    tree_plot_data,
    write_gallery_html,
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
    "make_balanced_tree_graph",
    "make_cave_man_graph",
    "make_circular_graph",
    "make_cubical_graph",
    "make_ladder_graph",
    "make_path_graph",
    "make_star_graph",
    "make_tadpole_graph",
    "make_total_ordering",
    "make_trivial_graph",
    "make_wheel_graph",
    "make_windmill_graph",
    "plot_graph",
    "plot_persistence_diagram",
    "plot_tree",
    "run_pipeline",
    "save_graph_plot",
    "save_persistence_diagram",
    "save_tree_plot",
    "scalar_layout",
    "simplify_contour_tree",
    "simplify_tree_by_persistence",
    "tree_plot_data",
    "write_gallery_html",
]
