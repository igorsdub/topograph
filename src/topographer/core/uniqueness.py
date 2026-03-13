from __future__ import annotations

from collections.abc import Hashable

import networkx as nx


def _get_scalar_values(G: nx.Graph, scalar_attr: str = "scalar") -> list[Hashable]:
    if not isinstance(G, nx.Graph):
        raise TypeError("Graph must be a networkx.Graph")

    values: list[Hashable] = []

    for node, data in G.nodes(data=True):
        if scalar_attr not in data:
            raise ValueError(f"Node {node} missing scalar attribute '{scalar_attr}'")

        values.append(data[scalar_attr])

    return values


def are_scalar_values_unique(G: nx.Graph, scalar_attr: str = "scalar") -> bool:
    values = _get_scalar_values(G, scalar_attr=scalar_attr)
    return len(values) == len(set(values))


def assert_unique_scalar_values(G: nx.Graph, scalar_attr: str = "scalar") -> bool:
    if not are_scalar_values_unique(G, scalar_attr=scalar_attr):
        raise ValueError("Duplicate scalar values detected")

    return True


__all__ = ["are_scalar_values_unique", "assert_unique_scalar_values"]
