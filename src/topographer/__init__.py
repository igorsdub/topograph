"""Topographer: minimal topology tools for graphs."""

from .api import run_pipeline
from .core import UnionFind, check_graph, ensure_total_order
from .models import ContourTree, MergeTree, PersistencePair, PipelineResult
from .persistence import compute_persistence_pairs
from .simplify import simplify_contour_tree
from .trees import compute_contour_tree, compute_join_tree, compute_split_tree

__all__ = [
    "ContourTree",
    "MergeTree",
    "PersistencePair",
    "PipelineResult",
    "UnionFind",
    "check_graph",
    "compute_contour_tree",
    "compute_join_tree",
    "compute_persistence_pairs",
    "compute_split_tree",
    "ensure_total_order",
    "run_pipeline",
    "simplify_contour_tree",
]
