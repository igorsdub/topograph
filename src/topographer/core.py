"""Core utilities for validation, ordering, and component tracking."""

from __future__ import annotations

from collections.abc import Iterable
from math import isfinite
from numbers import Real
from typing import Any

import networkx as nx


def check_graph(G: nx.Graph, scalar_attr: str) -> dict[Any, float]:
    """Validate that ``G`` is a graph with a numeric scalar on every node.

    Parameters
    ----------
    G:
        Input graph.
    scalar_attr:
        Node attribute storing the scalar field.

    Returns
    -------
    dict[Any, float]
        Mapping from node to scalar value.

    Raises
    ------
    TypeError
        If ``G`` is not an :class:`networkx.Graph` or a node value is not numeric.
    KeyError
        If a node is missing the scalar attribute.
    ValueError
        If a scalar value is not finite.
    """

    if not isinstance(G, nx.Graph):
        raise TypeError("G must be an instance of networkx.Graph.")

    scalars: dict[Any, float] = {}
    for node, data in G.nodes(data=True):
        if scalar_attr not in data:
            raise KeyError(f"Node {node!r} is missing the '{scalar_attr}' attribute.")

        value = data[scalar_attr]
        if not isinstance(value, Real) or isinstance(value, bool):
            raise TypeError(
                f"Node {node!r} has non-numeric scalar {value!r} "
                f"for attribute '{scalar_attr}'."
            )
        if not isfinite(float(value)):
            raise ValueError(f"Node {node!r} has a non-finite scalar value {value!r}.")

        scalars[node] = float(value)

    return scalars


def ensure_total_order(
    G: nx.Graph,
    scalar_attr: str,
    *,
    perturb: bool = True,
    epsilon: float = 1e-9,
) -> tuple[nx.Graph, dict[Any, float]]:
    """Return a copy of ``G`` with unique scalar values.

    Ties are broken deterministically using the node iteration order from the
    original graph. If ``perturb`` is ``False`` and ties are present, a
    ``ValueError`` is raised instead of modifying the values.

    Parameters
    ----------
    G:
        Input graph.
    scalar_attr:
        Node attribute storing the scalar field.
    perturb:
        Whether to perturb tied values slightly.
    epsilon:
        Increment used to separate tied values.

    Returns
    -------
    tuple[nx.Graph, dict[Any, float]]
        A copied graph with unique scalar values and the reordered scalar map.
    """

    scalars = check_graph(G, scalar_attr)
    ordered_graph = G.copy()
    node_order = {node: index for index, node in enumerate(G.nodes)}
    ordered_items = sorted(scalars.items(), key=lambda item: (item[1], node_order[item[0]]))

    has_ties = len({value for value in scalars.values()}) != len(scalars)
    if not has_ties:
        for node, value in scalars.items():
            ordered_graph.nodes[node][scalar_attr] = value
        return ordered_graph, dict(scalars)

    if not perturb:
        raise ValueError(
            "Scalar values are not unique; set perturb=True to enforce a total order."
        )

    unique_values = sorted({value for value in scalars.values()})
    positive_gaps = [
        upper - lower
        for lower, upper in zip(unique_values, unique_values[1:])
        if upper > lower
    ]
    min_gap = min(positive_gaps) if positive_gaps else None
    if min_gap is None:
        step = epsilon
    else:
        step = min(epsilon, min_gap / (len(scalars) + 1))

    ordered_scalars = {
        node: value + index * step
        for index, (node, value) in enumerate(ordered_items)
    }

    if len(set(ordered_scalars.values())) != len(ordered_scalars):
        ordered_scalars = {
            node: float(index)
            for index, (node, _value) in enumerate(ordered_items)
        }

    for node, value in ordered_scalars.items():
        ordered_graph.nodes[node][scalar_attr] = value

    return ordered_graph, ordered_scalars


class UnionFind:
    """A small deterministic union-find structure.

    The implementation intentionally keeps the API minimal and easy to inspect.
    No path compression or rank heuristics are used.
    """

    def __init__(self, items: Iterable[Any] | None = None) -> None:
        self.parent: dict[Any, Any] = {}
        if items is not None:
            for item in items:
                self.parent[item] = item

    def add(self, item: Any) -> None:
        """Add ``item`` as a singleton set if it is not already present."""

        self.parent.setdefault(item, item)

    def find(self, item: Any) -> Any:
        """Return the representative for ``item``."""

        if item not in self.parent:
            self.parent[item] = item
            return item

        parent = self.parent[item]
        while parent != self.parent[parent]:
            parent = self.parent[parent]
        return parent

    def union(self, first: Any, second: Any) -> Any:
        """Merge the sets containing ``first`` and ``second``.

        The representative of ``first`` becomes the new representative.
        """

        root_first = self.find(first)
        root_second = self.find(second)
        if root_first == root_second:
            return root_first
        self.parent[root_second] = root_first
        return root_first

    def components(self) -> dict[Any, set[Any]]:
        """Group the tracked items by component representative."""

        grouped: dict[Any, set[Any]] = {}
        for item in list(self.parent):
            root = self.find(item)
            grouped.setdefault(root, set()).add(item)
        return grouped
