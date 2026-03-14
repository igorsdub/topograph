from topographer.algorithms.augmentation import augment_join_tree, augment_split_tree
from topographer.algorithms.join_tree import compute_join_tree
from topographer.algorithms.split_tree import compute_split_tree
from topographer.examples import easy_star_graph
from topographer.models.tree import MergeTree


def test_split_and_join_tree_are_symmetric_on_star_graph():
    """Check split and join trees produce symmetric critical structure on stars."""
    graph = easy_star_graph(leaves=4)

    split = compute_split_tree(graph, scalar="scalar")
    join = compute_join_tree(graph, scalar="scalar")

    assert isinstance(split, MergeTree)
    assert isinstance(join, MergeTree)
    assert split.__class__ is join.__class__
    assert split.kind == "split"
    assert join.kind == "join"
    assert split.scalar == join.scalar == "scalar"
    assert split.root == min(graph.nodes())
    assert join.root == max(graph.nodes())
    assert len(split.critical_nodes) >= 2
    assert len(join.critical_nodes) >= 2


def test_split_and_join_augmented_preserve_graph_connectivity_on_star_graph():
    """Ensure augmented split/join trees preserve node and edge counts."""
    graph = easy_star_graph(leaves=5)

    split = augment_split_tree(compute_split_tree(graph, scalar="scalar"))
    join = augment_join_tree(compute_join_tree(graph, scalar="scalar"))

    assert split.tree.number_of_nodes() == graph.number_of_nodes()
    assert join.tree.number_of_nodes() == graph.number_of_nodes()
    assert split.tree.number_of_edges() == graph.number_of_edges()
    assert join.tree.number_of_edges() == graph.number_of_edges()
