from __future__ import annotations

"""Paired leaf-pruning construction of contour trees from split/join trees."""

from collections.abc import Hashable

import networkx as nx

from topographer.models.tree import MergeTree


def _edge_key(a: Hashable, b: Hashable) -> tuple[Hashable, Hashable]:
    ordered = sorted((a, b), key=repr)
    return ordered[0], ordered[1]


def _orient_path(path: list[Hashable], start: Hashable, end: Hashable) -> list[Hashable]:
    if path and path[0] == start and path[-1] == end:
        return path
    if path and path[0] == end and path[-1] == start:
        return list(reversed(path))
    return [start, end]


def _canonicalize_path(path: list[Hashable]) -> list[Hashable]:
    if len(path) <= 1:
        return path

    reversed_path = list(reversed(path))
    if tuple(map(repr, path)) <= tuple(map(repr, reversed_path)):
        return path
    return reversed_path


def _dedupe_consecutive(path: list[Hashable]) -> list[Hashable]:
    if not path:
        return path

    compact = [path[0]]
    for node in path[1:]:
        if node != compact[-1]:
            compact.append(node)
    return compact


def _build_working_tree(
    source: MergeTree,
) -> tuple[nx.Graph, dict[tuple[Hashable, Hashable], list[Hashable]]]:
    graph = nx.Graph()
    arcs: dict[tuple[Hashable, Hashable], list[Hashable]] = {}

    if source.arc_vertices:
        for edge, path in source.arc_vertices.items():
            key = _edge_key(edge[0], edge[1])
            graph.add_edge(*key)
            canonical = _canonicalize_path(list(path))
            existing = arcs.get(key)
            if existing is None or len(canonical) > len(existing):
                arcs[key] = canonical
    else:
        for a, b in source.graph.edges():
            key = _edge_key(a, b)
            graph.add_edge(*key)
            arcs[key] = [key[0], key[1]]

    graph.add_nodes_from(source.critical_nodes)
    for edge in graph.edges():
        key = _edge_key(edge[0], edge[1])
        arcs.setdefault(key, [key[0], key[1]])

    return graph, arcs


def _is_removable_leaf(
    leaf: Hashable,
    primary: nx.Graph,
    secondary: nx.Graph,
) -> bool:
    if primary.degree(leaf) != 1:
        return False

    if leaf not in secondary:
        return True

    return secondary.degree(leaf) <= 2


def _find_removable_leaf(
    primary: nx.Graph,
    secondary: nx.Graph,
) -> Hashable | None:
    candidates = sorted((node for node in primary.nodes() if primary.degree(node) == 1), key=repr)
    for leaf in candidates:
        if _is_removable_leaf(leaf, primary, secondary):
            return leaf
    return None


def _record_ct_arc(
    ct_graph: nx.Graph,
    ct_arcs: dict[tuple[Hashable, Hashable], list[Hashable]],
    start: Hashable,
    end: Hashable,
    path: list[Hashable],
) -> None:
    key = _edge_key(start, end)
    canonical = _canonicalize_path(_dedupe_consecutive(path))

    ct_graph.add_edge(*key)
    existing = ct_arcs.get(key)
    if existing is None or len(canonical) > len(existing):
        ct_arcs[key] = canonical


def _remove_leaf_arc(
    graph: nx.Graph,
    arcs: dict[tuple[Hashable, Hashable], list[Hashable]],
    leaf: Hashable,
) -> tuple[Hashable, list[Hashable]]:
    neighbor = next(iter(graph.neighbors(leaf)))
    key = _edge_key(leaf, neighbor)
    path = _orient_path(arcs.get(key, [leaf, neighbor]), start=leaf, end=neighbor)

    graph.remove_edge(leaf, neighbor)
    arcs.pop(key, None)
    if graph.degree(leaf) == 0:
        graph.remove_node(leaf)

    return neighbor, path


def _suppress_vertex_in_tree(
    graph: nx.Graph,
    arcs: dict[tuple[Hashable, Hashable], list[Hashable]],
    vertex: Hashable,
) -> None:
    if vertex not in graph:
        return

    while vertex in graph:
        degree = graph.degree(vertex)
        if degree == 0:
            graph.remove_node(vertex)
            return

        if degree == 1:
            neighbor = next(iter(graph.neighbors(vertex)))
            key = _edge_key(vertex, neighbor)
            graph.remove_edge(vertex, neighbor)
            arcs.pop(key, None)
            graph.remove_node(vertex)
            return

        if degree != 2:
            return

        left, right = list(graph.neighbors(vertex))
        left_key = _edge_key(left, vertex)
        right_key = _edge_key(vertex, right)

        left_path = _orient_path(arcs.get(left_key, [left, vertex]), start=left, end=vertex)
        right_path = _orient_path(arcs.get(right_key, [vertex, right]), start=vertex, end=right)
        merged_path = _dedupe_consecutive(left_path[:-1] + right_path)

        graph.remove_node(vertex)
        arcs.pop(left_key, None)
        arcs.pop(right_key, None)

        if left == right:
            return

        new_key = _edge_key(left, right)
        graph.add_edge(*new_key)
        arcs[new_key] = _canonicalize_path(merged_path)
        return


def _prune_leaf_into_ct(
    leaf: Hashable,
    primary_graph: nx.Graph,
    primary_arcs: dict[tuple[Hashable, Hashable], list[Hashable]],
    secondary_graph: nx.Graph,
    secondary_arcs: dict[tuple[Hashable, Hashable], list[Hashable]],
    ct_graph: nx.Graph,
    ct_arcs: dict[tuple[Hashable, Hashable], list[Hashable]],
) -> None:
    neighbor, path = _remove_leaf_arc(primary_graph, primary_arcs, leaf)
    _record_ct_arc(ct_graph, ct_arcs, leaf, neighbor, path)
    _suppress_vertex_in_tree(secondary_graph, secondary_arcs, leaf)


def compute_contour_tree_by_pruning(
    ST: MergeTree,
    JT: MergeTree,
) -> tuple[nx.Graph, dict[tuple[Hashable, Hashable], list[Hashable]]]:
    """Construct a contour tree by paired leaf pruning on split/join trees."""
    st_graph, st_arcs = _build_working_tree(ST)
    jt_graph, jt_arcs = _build_working_tree(JT)

    base_support: dict[tuple[Hashable, Hashable], int] = {}
    base_arcs: dict[tuple[Hashable, Hashable], list[Hashable]] = {}
    for source in (ST.arc_vertices, JT.arc_vertices):
        for edge, path in source.items():
            key = _edge_key(edge[0], edge[1])
            base_support[key] = base_support.get(key, 0) + 1
            canonical = _canonicalize_path(list(path))
            existing = base_arcs.get(key)
            if existing is None or len(canonical) > len(existing):
                base_arcs[key] = canonical

    ct_graph = nx.Graph()
    ct_arcs: dict[tuple[Hashable, Hashable], list[Hashable]] = {}

    while True:
        changed = False

        join_leaf = _find_removable_leaf(jt_graph, st_graph)
        if join_leaf is not None:
            _prune_leaf_into_ct(
                join_leaf,
                jt_graph,
                jt_arcs,
                st_graph,
                st_arcs,
                ct_graph,
                ct_arcs,
            )
            changed = True

        split_leaf = _find_removable_leaf(st_graph, jt_graph)
        if split_leaf is not None:
            _prune_leaf_into_ct(
                split_leaf,
                st_graph,
                st_arcs,
                jt_graph,
                jt_arcs,
                ct_graph,
                ct_arcs,
            )
            changed = True

        if not changed:
            break

    edge_support: dict[tuple[Hashable, Hashable], int] = dict(base_support)
    for edge, path in base_arcs.items():
        existing = ct_arcs.get(edge)
        if existing is None or len(path) > len(existing):
            ct_arcs[edge] = path

    for arcs in (st_arcs, jt_arcs):
        for edge, path in arcs.items():
            key = _edge_key(edge[0], edge[1])
            edge_support[key] = edge_support.get(key, 0) + 1
            existing = ct_arcs.get(key)
            candidate = _canonicalize_path(list(path))
            if existing is None or len(candidate) > len(existing):
                ct_arcs[key] = candidate

    final_graph = nx.Graph()
    final_nodes: set[Hashable] = set(ct_graph.nodes())
    for a, b in edge_support:
        final_nodes.add(a)
        final_nodes.add(b)
    final_graph.add_nodes_from(final_nodes)

    uf = nx.utils.UnionFind()
    for node in final_graph.nodes():
        uf[node]

    for a, b in sorted(ct_graph.edges(), key=lambda edge: (repr(edge[0]), repr(edge[1]))):
        key = _edge_key(a, b)
        if uf[key[0]] == uf[key[1]]:
            continue
        final_graph.add_edge(*key)
        uf.union(*key)

    ranked_remaining = sorted(
        edge_support,
        key=lambda edge: (
            edge_support[edge],
            len(ct_arcs.get(edge, [edge[0], edge[1]])),
            repr(edge[0]),
            repr(edge[1]),
        ),
        reverse=True,
    )
    for a, b in ranked_remaining:
        key = _edge_key(a, b)
        if uf[key[0]] == uf[key[1]]:
            continue
        final_graph.add_edge(*key)
        uf.union(*key)

    if final_graph.number_of_edges() == 0 and final_graph.number_of_nodes() > 0:
        representative = sorted(final_graph.nodes(), key=repr)[0]
        final_graph = nx.Graph()
        final_graph.add_node(representative)

    filtered_arcs: dict[tuple[Hashable, Hashable], list[Hashable]] = {}
    for a, b in final_graph.edges():
        key = _edge_key(a, b)
        filtered_arcs[key] = ct_arcs.get(key, [key[0], key[1]])

    return final_graph, filtered_arcs


__all__ = ["compute_contour_tree_by_pruning"]
