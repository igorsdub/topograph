from __future__ import annotations

"""Join-tree construction from a scalar graph."""

from collections.abc import Hashable

import networkx as nx

from topographer.algorithms._merge_rules import (
    SweepContext,
    finalize_components,
    handle_join_event,
)
from topographer.algorithms._sweep import sweep_ascending
from topographer.core.graph_check import check_graph
from topographer.models.tree import MergeTree


def compute_join_tree(
    G: nx.Graph,
    scalar: str = "scalar",
    *,
    require_connected: bool = True,
) -> MergeTree:
    """Compute the join tree using an ascending scalar sweep.

    Nodes are visited from low to high scalar value. Component merges and join
    events are tracked in a sweep context and exported as a ``JoinTree``.
    """
    check_graph(G, scalar_attr=scalar, require_connected=require_connected)

    context = SweepContext()

    def _visit(node: Hashable, seen: set[Hashable]):
        seen_neighbors = [neighbor for neighbor in G.neighbors(node) if neighbor in seen]
        handle_join_event(context, node=node, seen_neighbors=seen_neighbors)

    sweep_ascending(G, scalar=scalar, visit_fn=_visit)
    roots = finalize_components(context)
    root = roots[0] if roots else None

    critical_nodes = sorted(context.critical_nodes, key=lambda node: G.nodes[node][scalar])

    node_metadata = {
        node: {scalar: G.nodes[node][scalar]} for node in context.tree.nodes() if node in G.nodes
    }

    return MergeTree(
        graph=context.tree,
        root=root,
        critical_nodes=critical_nodes,
        scalar=scalar,
        kind="join",
        augmented=False,
        arc_vertices=context.arc_vertices,
        node_metadata=node_metadata,
    )


__all__ = ["compute_join_tree"]
