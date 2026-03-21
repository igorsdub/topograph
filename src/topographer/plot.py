"""Minimal plotting data helpers for graphs, trees, and persistence pairs."""

from __future__ import annotations

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


def plot_persistence_diagram(pairs: list[PersistencePair]) -> dict[str, object]:
    """Return point data for a persistence-diagram style plot."""

    points = [(pair.birth, pair.death, pair.persistence) for pair in pairs]
    return {"points": points}
