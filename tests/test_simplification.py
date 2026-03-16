import networkx as nx

from topographer.algorithms.contour_tree import compute_contour_tree
from topographer.algorithms.join_tree import compute_join_tree
from topographer.algorithms.simplification import (
    simplify_contour_tree,
    simplify_join_tree,
    simplify_split_tree,
)
from topographer.algorithms.split_tree import compute_split_tree
from topographer.examples import easy_star_graph


def _join_simplification_graph() -> nx.Graph:
    """Build a star graph fixture with scalar values suited for join simplification."""
    graph = nx.star_graph(4)
    graph.nodes[1]["scalar"] = 0.0
    graph.nodes[2]["scalar"] = 4.0
    graph.nodes[3]["scalar"] = 7.0
    graph.nodes[4]["scalar"] = 9.0
    graph.nodes[0]["scalar"] = 10.0
    return graph


def _mixed_simplification_graph() -> nx.Graph:
    """Build a mixed-branch graph fixture used for contour simplification checks."""
    graph = nx.Graph()
    graph.add_edges_from([(0, 1), (1, 2), (2, 3), (1, 4), (2, 5)])

    scalars = {
        0: 0.0,
        1: 1.0,
        2: 3.0,
        3: 2.0,
        4: 4.0,
        5: 5.0,
    }
    nx.set_node_attributes(graph, scalars, "scalar")
    return graph


def test_simplify_join_tree_prunes_low_persistence_leaf_arcs():
    """Verify join-tree simplification removes low-persistence leaf branches."""
    graph = _join_simplification_graph()
    JT = compute_join_tree(graph, scalar="scalar")

    simplified = simplify_join_tree(JT, threshold=5.0)

    assert set(simplified.graph.nodes()) == {0, 1, 2}
    assert {tuple(sorted(edge)) for edge in simplified.graph.edges()} == {(0, 1), (0, 2)}


def test_simplify_split_tree_prunes_low_persistence_leaf_arcs():
    """Verify split-tree simplification removes low-persistence leaf branches."""
    graph = easy_star_graph(4)
    ST = compute_split_tree(graph, scalar="scalar")

    simplified = simplify_split_tree(ST, threshold=3.0)

    assert set(simplified.graph.nodes()) == {0, 3, 4}
    assert {tuple(sorted(edge)) for edge in simplified.graph.edges()} == {(0, 3), (0, 4)}


def test_simplify_contour_tree_simplifies_split_join_then_recomputes_contour_tree():
    """Ensure contour simplification updates split/join trees and recomputes contour edges."""
    graph = _mixed_simplification_graph()
    CT = compute_contour_tree(graph, scalar="scalar")

    simplified = simplify_contour_tree(CT, threshold=2.0)

    assert simplified.ST is not None
    assert simplified.JT is not None
    assert simplified.ST.augmented is True
    assert simplified.JT.augmented is True
    assert simplified.JT.graph.number_of_nodes() <= CT.JT.graph.number_of_nodes()
    assert simplified.ST.graph.number_of_nodes() <= CT.ST.graph.number_of_nodes()

    original_edges = {tuple(sorted(edge)) for edge in CT.graph.edges()}
    simplified_edges = {tuple(sorted(edge)) for edge in simplified.graph.edges()}
    assert len(simplified_edges) <= len(original_edges)
