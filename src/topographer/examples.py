from __future__ import annotations

"""Reusable graph fixtures for testing and demos.

Graphs are grouped by rough difficulty:
- easy: small, simple topologies
- medium: richer branching/lattice structures
- hard: denser or mixed structures

All *valid* examples include unique numeric ``scalar`` node attributes.
"""

import networkx as nx


def _assign_unique_scalar_by_node_order(graph: nx.Graph) -> nx.Graph:
    for index, node in enumerate(graph.nodes()):
        graph.nodes[node]["scalar"] = float(index)
    return graph


def _assign_non_unique_scalar_values(graph: nx.Graph) -> nx.Graph:
    for index, node in enumerate(graph.nodes()):
        graph.nodes[node]["scalar"] = float(index)

    nodes = list(graph.nodes())

    if len(nodes) >= 2:
        graph.nodes[nodes[1]]["scalar"] = graph.nodes[nodes[0]]["scalar"]

    return graph


def easy_path_graph(n: int = 5) -> nx.Graph:
    graph = nx.path_graph(n)
    return _assign_unique_scalar_by_node_order(graph)


def easy_star_graph(leaves: int = 6) -> nx.Graph:
    graph = nx.star_graph(leaves)
    return _assign_unique_scalar_by_node_order(graph)


def medium_binary_tree_graph(height: int = 3) -> nx.Graph:
    graph = nx.balanced_tree(r=2, h=height)
    return _assign_unique_scalar_by_node_order(graph)


def medium_grid_graph(rows: int = 3, cols: int = 4) -> nx.Graph:
    graph = nx.grid_2d_graph(rows, cols)
    return _assign_unique_scalar_by_node_order(graph)


def hard_barbell_graph(clique_size: int = 4, path_length: int = 3) -> nx.Graph:
    graph = nx.barbell_graph(m1=clique_size, m2=path_length)
    return _assign_unique_scalar_by_node_order(graph)


def hard_lollipop_graph(clique_size: int = 5, path_length: int = 5) -> nx.Graph:
    graph = nx.lollipop_graph(m=clique_size, n=path_length)
    return _assign_unique_scalar_by_node_order(graph)


def invalid_missing_scalar_graph() -> nx.Graph:
    graph = nx.path_graph(4)
    graph.nodes[0]["scalar"] = 0.0
    graph.nodes[1]["scalar"] = 1.0
    graph.nodes[2]["scalar"] = 2.0
    return graph


def invalid_duplicate_scalar_graph() -> nx.Graph:
    graph = nx.path_graph(4)
    return _assign_non_unique_scalar_values(graph)


def invalid_disconnected_graph() -> nx.Graph:
    graph = nx.Graph()
    graph.add_nodes_from([0, 1, 2, 3])
    graph.add_edge(0, 1)
    graph.add_edge(2, 3)
    return _assign_unique_scalar_by_node_order(graph)


def get_graph_options() -> dict[str, nx.Graph]:
    """Return a ready-to-use catalog of example graphs for tests."""

    return {
        "easy_path": easy_path_graph(),
        "easy_star": easy_star_graph(),
        "medium_binary_tree": medium_binary_tree_graph(),
        "medium_grid": medium_grid_graph(),
        "hard_barbell": hard_barbell_graph(),
        "hard_lollipop": hard_lollipop_graph(),
        "invalid_missing_scalar": invalid_missing_scalar_graph(),
        "invalid_duplicate_scalar": invalid_duplicate_scalar_graph(),
        "invalid_disconnected": invalid_disconnected_graph(),
    }


__all__ = [
    "easy_path_graph",
    "easy_star_graph",
    "medium_binary_tree_graph",
    "medium_grid_graph",
    "hard_barbell_graph",
    "hard_lollipop_graph",
    "invalid_missing_scalar_graph",
    "invalid_duplicate_scalar_graph",
    "invalid_disconnected_graph",
    "get_graph_options",
]
