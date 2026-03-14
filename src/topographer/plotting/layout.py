from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import networkx as nx


def planar_layout(
    tree: nx.Graph[Any],
    *,
    scalar: str = "scalar",
    root: Any | None = None,
    x_mode: str = "leaf_span",
) -> dict[Any, tuple[float, float]]:
    """Compute planar plotting positions for a tree.

    Y coordinates are read from node scalar values. X coordinates are
    computed by the configured ``x_mode`` strategy.
    """
    _validate_tree_input(tree, scalar)

    resolved_root = _resolve_root(tree, scalar=scalar, root=root)
    _, children = _build_rooted_view(tree, resolved_root)

    y_pos = _compute_y_positions(tree, scalar=scalar)

    if x_mode == "leaf_span":
        x_pos = _compute_x_leaf_span(resolved_root, children)
    else:
        raise ValueError(f"Unknown x_mode: {x_mode!r}")

    return {node: (x_pos[node], y_pos[node]) for node in tree.nodes}


def assign_planar_layout(
    tree: nx.Graph[Any],
    *,
    scalar: str = "scalar",
    root: Any | None = None,
    x_mode: str = "leaf_span",
    x_attr: str = "layout_x",
    y_attr: str = "layout_y",
    pos_attr: str = "pos",
) -> dict[Any, tuple[float, float]]:
    """Compute planar layout and assign coordinates to node attributes."""
    pos = planar_layout(tree, scalar=scalar, root=root, x_mode=x_mode)

    for node, (x_coord, y_coord) in pos.items():
        tree.nodes[node][x_attr] = x_coord
        tree.nodes[node][y_attr] = y_coord
        tree.nodes[node][pos_attr] = (x_coord, y_coord)

    return pos


def _validate_tree_input(tree: nx.Graph[Any], scalar: str) -> None:
    if tree.number_of_nodes() == 0:
        raise ValueError("tree must not be empty")

    if not nx.is_tree(tree):
        raise ValueError("tree must be a connected acyclic graph")

    missing = [node for node, data in tree.nodes(data=True) if scalar not in data]
    if missing:
        preview = missing[:5]
        raise ValueError(f"Missing scalar attribute {scalar!r} on nodes: {preview}")


def _resolve_root(
    tree: nx.Graph[Any],
    *,
    scalar: str,
    root: Any | None,
) -> Any:
    if root is not None:
        if root not in tree:
            raise ValueError(f"Root {root!r} is not in tree")
        return root

    return max(tree.nodes, key=lambda node: tree.nodes[node][scalar])


def _build_rooted_view(
    tree: nx.Graph[Any],
    root: Any,
) -> tuple[dict[Any, Any | None], dict[Any, list[Any]]]:
    parent: dict[Any, Any | None] = {root: None}
    children: dict[Any, list[Any]] = {node: [] for node in tree.nodes}

    stack = [root]
    while stack:
        node = stack.pop()
        for neighbor in tree.neighbors(node):
            if neighbor == parent[node]:
                continue
            parent[neighbor] = node
            children[node].append(neighbor)
            stack.append(neighbor)

    return parent, children


def _compute_y_positions(tree: nx.Graph[Any], *, scalar: str) -> dict[Any, float]:
    return {node: float(tree.nodes[node][scalar]) for node in tree.nodes}


def _compute_x_leaf_span(
    root: Any,
    children: Mapping[Any, list[Any]],
) -> dict[Any, float]:
    """Assign x coordinates using descendant leaf span.

    Leaves get consecutive x coordinates; internal nodes are centered at
    the midpoint of their children span.
    """
    x_pos: dict[Any, float] = {}
    next_leaf_x = 0

    def visit(node: Any) -> float:
        nonlocal next_leaf_x

        node_children = children[node]
        if not node_children:
            x_coord = float(next_leaf_x)
            x_pos[node] = x_coord
            next_leaf_x += 1
            return x_coord

        child_x = [visit(child) for child in node_children]
        x_coord = (min(child_x) + max(child_x)) / 2.0
        x_pos[node] = x_coord
        return x_coord

    visit(root)
    return x_pos
