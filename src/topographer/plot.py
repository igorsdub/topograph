"""Minimal plotting data helpers for trees."""

from __future__ import annotations

import networkx as nx


def scalar_layout(
    G: nx.Graph,
    scalar: str,
) -> dict[object, tuple[float, float]]:
    """Place nodes by index on x and scalar value on y."""

    ordered_nodes = sorted(G.nodes, key=lambda node: (float(G.nodes[node][scalar]), str(node)))
    return {
        node: (float(index), float(G.nodes[node][scalar]))
        for index, node in enumerate(ordered_nodes)
    }


def tree_plot_data(
    G: nx.Graph,
    scalar: str,
) -> dict[str, object]:
    """Return lightweight plotting data without depending on a graphics library."""

    return {
        "positions": scalar_layout(G, scalar),
        "edges": list(G.edges()),
        "nodes": list(G.nodes()),
    }
