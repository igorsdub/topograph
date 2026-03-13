from topographer.algorithms.augmentation import augment_join_tree, augment_split_tree
from topographer.algorithms.join_tree import compute_join_tree
from topographer.algorithms.split_tree import compute_split_tree
from topographer.examples import easy_path_graph


def test_split_join_results_provide_inputs_for_contour_stage():
    graph = easy_path_graph(6)

    split = compute_split_tree(graph, scalar="scalar")
    join = compute_join_tree(graph, scalar="scalar")

    assert split.scalar == join.scalar == "scalar"
    assert split.root in graph.nodes
    assert join.root in graph.nodes
    assert split.tree.number_of_nodes() > 0
    assert join.tree.number_of_nodes() > 0


def test_augmented_split_join_retain_vertex_traces_for_contour_augmentation():
    graph = easy_path_graph(6)

    split = augment_split_tree(compute_split_tree(graph, scalar="scalar"))
    join = augment_join_tree(compute_join_tree(graph, scalar="scalar"))

    assert split.arc_vertices
    assert join.arc_vertices

    split_path_vertices = {vertex for path in split.arc_vertices.values() for vertex in path}
    join_path_vertices = {vertex for path in join.arc_vertices.values() for vertex in path}

    assert set(graph.nodes()).issubset(split_path_vertices)
    assert set(graph.nodes()).issubset(join_path_vertices)
