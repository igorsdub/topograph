from __future__ import annotations

from collections.abc import Hashable
from dataclasses import dataclass, field
from typing import Any

import networkx as nx

from topographer.core.unionfind import UnionFind


def _new_component_head() -> dict[Hashable, Hashable]:
    return {}


def _new_component_buffer() -> dict[Hashable, list[Hashable]]:
    return {}


def _new_critical_nodes() -> set[Hashable]:
    return set()


def _new_arc_vertices() -> dict[tuple[Hashable, Hashable], list[Hashable]]:
    return {}


def _new_tree() -> nx.Graph[Any]:
    return nx.Graph()


@dataclass(slots=True)
class SweepContext:
    tree: nx.Graph[Any] = field(default_factory=_new_tree)
    uf: UnionFind = field(default_factory=UnionFind)
    component_head: dict[Hashable, Hashable] = field(default_factory=_new_component_head)
    component_buffer: dict[Hashable, list[Hashable]] = field(default_factory=_new_component_buffer)
    critical_nodes: set[Hashable] = field(default_factory=_new_critical_nodes)
    arc_vertices: dict[tuple[Hashable, Hashable], list[Hashable]] = field(
        default_factory=_new_arc_vertices
    )


def _edge_key(a: Hashable, b: Hashable) -> tuple[Hashable, Hashable]:
    ordered = sorted((a, b), key=repr)
    return ordered[0], ordered[1]


def _add_arc(
    context: SweepContext,
    start: Hashable,
    end: Hashable,
    intermediates: list[Hashable] | None = None,
):
    middle = intermediates if intermediates is not None else []
    path = [start, *middle, end]

    if start != end:
        context.tree.add_edge(start, end)
    else:
        context.tree.add_node(start)

    if start != end:
        context.arc_vertices[_edge_key(start, end)] = path


def _unique_roots(context: SweepContext, neighbors: list[Hashable]) -> list[Hashable]:
    roots: set[Hashable] = set()

    for neighbor in neighbors:
        roots.add(context.uf.find(neighbor))

    return list(roots)


def _initialize_component(context: SweepContext, node: Hashable):
    context.uf.make_set(node)
    root = context.uf.find(node)
    context.component_head[root] = node
    context.component_buffer[root] = []
    context.critical_nodes.add(node)


def _absorb_node_into_component(
    context: SweepContext,
    node: Hashable,
    root: Hashable,
):
    root = context.uf.find(root)
    head = context.component_head.pop(root)
    buffer = context.component_buffer.pop(root)

    context.uf.make_set(node)
    merged_root = context.uf.union(root, node)
    merged_root = context.uf.find(merged_root)

    buffer.append(node)
    context.component_head[merged_root] = head
    context.component_buffer[merged_root] = buffer


def _merge_components_at_critical(
    context: SweepContext,
    node: Hashable,
    roots: list[Hashable],
):
    context.critical_nodes.add(node)

    for root in roots:
        canonical_root = context.uf.find(root)
        head = context.component_head.pop(canonical_root)
        buffer = context.component_buffer.pop(canonical_root)
        _add_arc(context, start=head, end=node, intermediates=buffer)

    context.uf.make_set(node)
    merged_root = context.uf.find(node)

    for root in roots:
        merged_root = context.uf.union(merged_root, root)

    merged_root = context.uf.find(merged_root)
    context.component_head[merged_root] = node
    context.component_buffer[merged_root] = []


def handle_join_event(
    context: SweepContext,
    node: Hashable,
    seen_neighbors: list[Hashable],
):
    roots = _unique_roots(context, seen_neighbors)

    if not roots:
        _initialize_component(context, node)
        return

    if len(roots) == 1:
        _absorb_node_into_component(context, node=node, root=roots[0])
        return

    _merge_components_at_critical(context, node=node, roots=roots)


def handle_split_event(
    context: SweepContext,
    node: Hashable,
    seen_neighbors: list[Hashable],
):
    roots = _unique_roots(context, seen_neighbors)

    if not roots:
        _initialize_component(context, node)
        return

    if len(roots) == 1:
        _absorb_node_into_component(context, node=node, root=roots[0])
        return

    _merge_components_at_critical(context, node=node, roots=roots)


def finalize_components(context: SweepContext) -> list[Hashable]:
    roots_to_return: list[Hashable] = []

    for root in list(context.component_head.keys()):
        canonical_root = context.uf.find(root)
        if canonical_root != root:
            continue

        head = context.component_head[canonical_root]
        buffer = context.component_buffer[canonical_root]

        if not buffer:
            context.tree.add_node(head)
            roots_to_return.append(head)
            continue

        final_node = buffer[-1]
        middle = buffer[:-1]
        context.critical_nodes.add(final_node)
        _add_arc(context, start=head, end=final_node, intermediates=middle)
        context.component_head[canonical_root] = final_node
        context.component_buffer[canonical_root] = []
        roots_to_return.append(final_node)

    return roots_to_return


__all__ = [
    "SweepContext",
    "handle_join_event",
    "handle_split_event",
    "finalize_components",
]
