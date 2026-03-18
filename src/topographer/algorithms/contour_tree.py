from __future__ import annotations

"""Contour-tree construction from split and join trees."""

import networkx as nx

from topographer.algorithms.contour_prune import compute_contour_tree_by_pruning
from topographer.algorithms.join_tree import compute_join_tree
from topographer.algorithms.split_tree import compute_split_tree
from topographer.models.tree import ContourTree, MergeTree


def compute_contour_tree_from_split_join(
    ST: MergeTree,
    JT: MergeTree,
) -> ContourTree:
    """Merge split and join trees and reduce degree-2 regular nodes.

    The resulting contour tree keeps critical nodes and arc-vertex traces needed
    by downstream persistence and simplification routines.
    """
    if not ST.augmented or not JT.augmented:
        raise ValueError(
            "Contour tree construction requires augmented split and join trees; "
            "compute them with augment=True"
        )

    ct_graph, ct_arc_vertices = compute_contour_tree_by_pruning(ST, JT)

    critical_nodes = sorted(ct_graph.nodes(), key=repr)

    node_metadata = dict(ST.node_metadata)
    node_metadata.update(JT.node_metadata)

    return ContourTree(
        graph=ct_graph,
        scalar=ST.scalar,
        split_tree=ST,
        join_tree=JT,
        augmented=True,
        critical_nodes=critical_nodes,
        arc_vertices=ct_arc_vertices,
        node_metadata=node_metadata,
    )


def compute_contour_tree(
    graph: nx.Graph,
    scalar: str = "scalar",
    *,
    require_connected: bool = True,
) -> ContourTree:
    """Compute a contour tree directly from an input scalar graph."""
    ST = compute_split_tree(
        graph,
        scalar=scalar,
        require_connected=require_connected,
        augment=True,
    )
    JT = compute_join_tree(
        graph,
        scalar=scalar,
        require_connected=require_connected,
        augment=True,
    )

    return compute_contour_tree_from_split_join(ST, JT)


__all__ = ["compute_contour_tree", "compute_contour_tree_from_split_join"]
