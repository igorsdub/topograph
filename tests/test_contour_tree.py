import networkx as nx
import pytest

from topographer.algorithms.augmentation import augment_contour_tree
from topographer.algorithms.contour_merge import merge_split_join_trees
from topographer.algorithms.contour_tree import (
    compute_contour_tree,
    compute_contour_tree_from_split_join,
)
from topographer.algorithms.deaugmentation import deaugment_merge_tree
from topographer.algorithms.degree_reduction import reduce_degree_two_nodes
from topographer.algorithms.join_tree import compute_join_tree
from topographer.algorithms.split_tree import compute_split_tree
from topographer.examples import easy_path_graph, easy_star_graph
from topographer.models.tree import MergeTree
from topographer.transforms.perturb import perturb_ties
from topographer.workflows.contour_pipeline import medium_example_graph


def test_merge_split_join_trees_combines_edges_and_traces():
    """Verify split/join merge preserves expected edge set and arc trace on paths."""
    graph = easy_path_graph(6)

    ST = compute_split_tree(graph, scalar="scalar", augment=False)
    JT = compute_join_tree(graph, scalar="scalar", augment=False)
    merged_tree, merged_arc_vertices = merge_split_join_trees(ST, JT)

    assert set(merged_tree.nodes()) == {0, 5}
    normalized_edges = {tuple(sorted(edge)) for edge in merged_tree.edges()}
    assert normalized_edges == {(0, 5)}
    assert merged_arc_vertices[(0, 5)] == [0, 1, 2, 3, 4, 5]


def test_reduce_degree_two_nodes_suppresses_chain_vertices():
    """Check degree-2 reduction contracts a simple chain into one arc."""
    graph = nx.Graph()
    graph.add_edge("a", "b")
    graph.add_edge("b", "c")
    graph.add_edge("c", "d")

    arc_vertices = {
        ("a", "b"): ["a", "b"],
        ("b", "c"): ["b", "c"],
        ("c", "d"): ["c", "d"],
    }

    reduced, reduced_arc_vertices = reduce_degree_two_nodes(graph, arc_vertices)

    assert set(reduced.nodes()) == {"a", "d"}
    assert set(reduced.edges()) == {("a", "d")}
    assert reduced_arc_vertices[("a", "d")] == ["a", "b", "c", "d"]


def test_compute_contour_tree_from_split_join_returns_augmented_tree():
    """Ensure contour tree built from split/join context carries augmented arc traces."""
    graph = easy_star_graph(6)

    ST = compute_split_tree(graph, scalar="scalar")
    JT = compute_join_tree(graph, scalar="scalar")
    CT = compute_contour_tree_from_split_join(ST, JT)

    assert isinstance(ST, MergeTree)
    assert isinstance(JT, MergeTree)
    assert ST.kind == "split"
    assert JT.kind == "join"
    assert CT.scalar == "scalar"
    assert ST.augmented is True
    assert JT.augmented is True
    assert CT.augmented is True
    assert CT.graph.number_of_nodes() > 0
    assert CT.graph.number_of_edges() > 0
    assert CT.ST is ST
    assert CT.JT is JT


def test_compute_contour_tree_from_split_join_is_acyclic_on_medium_example():
    """Regression: merged split/join contour skeleton must be cycle-free."""
    graph = medium_example_graph()
    perturb_ties(graph, scalar="scalar", output_scalar="scalar", inplace=True)

    ST = compute_split_tree(graph, scalar="scalar")
    JT = compute_join_tree(graph, scalar="scalar")
    CT = compute_contour_tree_from_split_join(ST, JT)

    assert nx.is_tree(CT.graph)


def test_compute_contour_tree_from_split_join_requires_augmented_inputs():
    """Contour-tree merge requires augmented split and join trees."""
    graph = easy_path_graph(6)

    ST = compute_split_tree(graph, scalar="scalar", augment=False)
    JT = compute_join_tree(graph, scalar="scalar", augment=False)

    with pytest.raises(ValueError, match="requires augmented split and join trees"):
        compute_contour_tree_from_split_join(ST, JT)


def test_deaugment_merge_tree_recovers_compact_critical_skeleton():
    """Deaugmentation should collapse augmented split/join tree back to critical arcs."""
    graph = easy_path_graph(6)
    augmented = compute_join_tree(graph, scalar="scalar")

    compact = deaugment_merge_tree(augmented)

    assert compact.augmented is False
    assert set(compact.graph.nodes()) == {0, 5}
    assert set(compact.graph.edges()) == {(0, 5)}


def test_augment_contour_tree_keeps_all_vertices_on_path_graph():
    """Ensure contour-tree augmentation restores intermediate vertices for path input."""
    graph = easy_path_graph(6)

    CT = compute_contour_tree(graph, scalar="scalar")
    augmented = augment_contour_tree(CT)

    assert CT.augmented is True
    assert augmented.augmented is True
    assert set(graph.nodes()).issubset(augmented.tree.nodes())
    assert augmented.tree.number_of_edges() == graph.number_of_edges()
