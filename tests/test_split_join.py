from topographer.algorithms.augmentation import augment_join_tree, augment_split_tree
from topographer.algorithms.join_tree import compute_join_tree
from topographer.algorithms.split_tree import compute_split_tree
from topographer.examples import easy_star_graph


def test_split_and_join_tree_are_symmetric_on_star_graph():
    graph = easy_star_graph(leaves=4)

    split = compute_split_tree(graph, scalar="scalar")
    join = compute_join_tree(graph, scalar="scalar")

    assert split.scalar == join.scalar == "scalar"
    assert split.root == min(graph.nodes())
    assert join.root == max(graph.nodes())
    assert len(split.critical_nodes) >= 2
    assert len(join.critical_nodes) >= 2


def test_split_and_join_augmented_preserve_graph_connectivity_on_star_graph():
    graph = easy_star_graph(leaves=5)

    split = augment_split_tree(compute_split_tree(graph, scalar="scalar"))
    join = augment_join_tree(compute_join_tree(graph, scalar="scalar"))

    assert split.tree.number_of_nodes() == graph.number_of_nodes()
    assert join.tree.number_of_nodes() == graph.number_of_nodes()
    assert split.tree.number_of_edges() == graph.number_of_edges()
    assert join.tree.number_of_edges() == graph.number_of_edges()
