import pytest

from topographer.algorithms.contour_tree import compute_contour_tree
from topographer.algorithms.join_tree import compute_join_tree
from topographer.algorithms.persistence import (
    compute_persistence_from_contour_tree,
    compute_persistence_from_split_join,
)
from topographer.algorithms.split_tree import compute_split_tree
from topographer.examples import easy_path_graph
from topographer.models.tree import MergeTree


def test_compute_persistence_from_split_join_on_path_graph():
    """Check split/join-based persistence returns one expected pair on a path."""
    graph = easy_path_graph(6)
    ST = compute_split_tree(graph, scalar="scalar")
    JT = compute_join_tree(graph, scalar="scalar")

    assert isinstance(ST, MergeTree)
    assert isinstance(JT, MergeTree)
    assert ST.kind == "split"
    assert JT.kind == "join"

    result = compute_persistence_from_split_join(ST, JT)

    assert result.scalar == "scalar"
    assert len(result.pairs) == 1

    pair = result.pairs[0]
    assert {pair.birth, pair.death} == {0, 5}
    assert pair.birth_scalar == pytest.approx(0.0)
    assert pair.death_scalar == pytest.approx(5.0)
    assert pair.persistence == pytest.approx(5.0)


def test_compute_persistence_from_contour_tree_on_path_graph():
    """Check contour-tree-based persistence returns one expected pair on a path."""
    graph = easy_path_graph(6)
    CT = compute_contour_tree(graph, scalar="scalar")

    result = compute_persistence_from_contour_tree(CT)

    assert result.scalar == "scalar"
    assert len(result.pairs) == 1

    pair = result.pairs[0]
    assert {pair.birth, pair.death} == {0, 5}
    assert pair.birth_scalar == pytest.approx(0.0)
    assert pair.death_scalar == pytest.approx(5.0)
    assert pair.persistence == pytest.approx(5.0)


def test_compute_persistence_from_contour_tree_requires_split_join_context():
    """Ensure contour-tree persistence requires both split and join tree context."""
    graph = easy_path_graph(6)
    ST = compute_split_tree(graph, scalar="scalar")
    JT = compute_join_tree(graph, scalar="scalar")

    CT = compute_contour_tree(graph, scalar="scalar")
    CT.ST = ST
    CT.JT = None

    with pytest.raises(ValueError, match="requires both split_tree and join_tree"):
        compute_persistence_from_contour_tree(CT)

    CT.JT = JT
    CT.ST = None

    with pytest.raises(ValueError, match="requires both split_tree and join_tree"):
        compute_persistence_from_contour_tree(CT)
