"""Deterministic example graphs with scalar values on every node."""

from __future__ import annotations

from collections.abc import Iterable

import networkx as nx

__all__ = [
    "make_balanced_tree_graph",
    "make_cave_man_graph",
    "make_circular_graph",
    "make_cubical_graph",
    "make_ladder_graph",
    "make_path_graph",
    "make_star_graph",
    "make_tadpole_graph",
    "make_trivial_graph",
    "make_wheel_graph",
    "make_windmill_graph",
]


def _sorted_nodes(graph: nx.Graph) -> list[object]:
    return sorted(graph.nodes, key=repr)


def _set_scalar_values(
    graph: nx.Graph,
    values: Iterable[float],
    scalar: str,
) -> nx.Graph:
    node_values = dict(zip(_sorted_nodes(graph), values, strict=True))
    nx.set_node_attributes(graph, node_values, scalar)
    return graph


def _set_linear_scalars(graph: nx.Graph, scalar: str) -> nx.Graph:
    nodes = _sorted_nodes(graph)
    if len(nodes) == 1:
        graph.nodes[nodes[0]][scalar] = 0.0
        return graph

    node_values = {
        node: index / (len(nodes) - 1)
        for index, node in enumerate(nodes)
    }
    nx.set_node_attributes(graph, node_values, scalar)
    return graph


def make_trivial_graph(scalar: str = "scalar") -> nx.Graph:
    """Return a single-node graph."""

    return _set_scalar_values(nx.path_graph(1), [0.0], scalar)


def make_path_graph(scalar: str = "scalar") -> nx.Graph:
    """Return a path graph with a simple non-monotone scalar field."""

    return _set_scalar_values(nx.path_graph(5), [0.0, 0.6, 0.2, 1.0, 0.3], scalar)


def make_circular_graph(scalar: str = "scalar") -> nx.Graph:
    """Return a cycle graph."""

    return _set_linear_scalars(nx.cycle_graph(6), scalar)


def make_star_graph(scalar: str = "scalar") -> nx.Graph:
    """Return a star graph."""

    return _set_scalar_values(nx.star_graph(4), [0.2, 0.8, 0.0, 0.4, 1.0], scalar)


def make_tadpole_graph(scalar: str = "scalar") -> nx.Graph:
    """Return a tadpole graph."""

    return _set_linear_scalars(nx.tadpole_graph(4, 3), scalar)


def make_wheel_graph(scalar: str = "scalar") -> nx.Graph:
    """Return a wheel graph."""

    return _set_linear_scalars(nx.wheel_graph(6), scalar)


def make_cubical_graph(scalar: str = "scalar") -> nx.Graph:
    """Return a cubical graph."""

    return _set_linear_scalars(nx.cubical_graph(), scalar)


def make_windmill_graph(scalar: str = "scalar") -> nx.Graph:
    """Return a small connected windmill graph."""

    return _set_linear_scalars(nx.windmill_graph(3, 4), scalar)


def make_cave_man_graph(scalar: str = "scalar") -> nx.Graph:
    """Return a connected cave man graph."""

    return _set_linear_scalars(nx.connected_caveman_graph(2, 3), scalar)


def make_ladder_graph(scalar: str = "scalar") -> nx.Graph:
    """Return a ladder graph."""

    return _set_linear_scalars(nx.ladder_graph(4), scalar)


def make_balanced_tree_graph(scalar: str = "scalar") -> nx.Graph:
    """Return a small balanced tree graph."""

    return _set_linear_scalars(nx.balanced_tree(r=2, h=2), scalar)
