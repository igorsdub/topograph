from __future__ import annotations

"""Split-tree construction from a scalar graph."""

from collections.abc import Hashable

import networkx as nx

from topographer.algorithms._merge_rules import (
    SweepContext,
    finalize_components,
    handle_split_event,
)
from topographer.algorithms._sweep import sweep_descending
from topographer.algorithms.augmentation import augment_split_tree
from topographer.core.graph_check import check_graph
from topographer.models.tree import MergeTree


def compute_split_tree(
    G: nx.Graph,
    scalar: str = "scalar",
    *,
    require_connected: bool = True,
    augment: bool = True,
) -> MergeTree:
    """Compute the split tree using a descending scalar sweep.

    Nodes are visited from high to low scalar value. Component merges and split
    events are tracked in a sweep context and exported as a ``SplitTree``.
    """
    check_graph(G, scalar_attr=scalar, require_connected=require_connected)

    context = SweepContext()

    def _visit(node: Hashable, seen: set[Hashable]):
        seen_neighbors = [neighbor for neighbor in G.neighbors(node) if neighbor in seen]
        handle_split_event(context, node=node, seen_neighbors=seen_neighbors)

    sweep_descending(G, scalar=scalar, visit_fn=_visit)
    roots = finalize_components(context)
    root = roots[0] if roots else None

    critical_nodes = sorted(
        context.critical_nodes,
        key=lambda node: G.nodes[node][scalar],
        reverse=True,
    )

    node_metadata = {node: {scalar: G.nodes[node][scalar]} for node in G.nodes()}

    base_result = MergeTree(
        graph=context.tree,
        root=root,
        critical_nodes=critical_nodes,
        scalar=scalar,
        kind="split",
        augmented=False,
        arc_vertices=context.arc_vertices,
        node_metadata=node_metadata,
    )

    if not augment:
        return base_result

    return augment_split_tree(base_result)


__all__ = ["compute_split_tree"]
