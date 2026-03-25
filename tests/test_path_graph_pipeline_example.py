"""Tests for the step-by-step path graph example."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import networkx as nx

from topographer import (
    check_graph,
    compute_contour_tree_from_trees,
    compute_join_tree,
    compute_persistence,
    compute_split_tree,
    ensure_total_order,
    make_path_graph,
    simplify_tree_by_persistence,
)


def load_path_graph_pipeline_module():
    """Load the example module from its file path."""

    root = Path(__file__).resolve().parents[1]
    module_path = root / "examples" / "path_graph_pipeline.py"
    spec = importlib.util.spec_from_file_location("path_graph_pipeline_example", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load examples/path_graph_pipeline.py")

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_path_graph_builder_returns_connected_graph_with_unit_interval_scalars() -> None:
    graph = make_path_graph()

    assert isinstance(graph, nx.Graph)
    assert nx.is_connected(graph)
    assert all(0.0 <= graph.nodes[node]["scalar"] <= 1.0 for node in graph.nodes)


def test_path_graph_example_pipeline_produces_expected_outputs() -> None:
    graph = make_path_graph()

    validated_scalars = check_graph(graph, "scalar")
    ordered_graph, ordered_scalars = ensure_total_order(graph, "scalar")
    join_tree = compute_join_tree(ordered_graph, "scalar")
    split_tree = compute_split_tree(ordered_graph, "scalar")
    contour_tree = compute_contour_tree_from_trees(split_tree, join_tree)
    persistence_pairs = compute_persistence(contour_tree, scalar="scalar")
    simplified_contour_tree = simplify_tree_by_persistence(
        contour_tree,
        persistence_pairs,
        threshold=0.5,
    )

    assert validated_scalars == {0: 0.0, 1: 0.6, 2: 0.2, 3: 1.0, 4: 0.3}
    assert ordered_scalars == validated_scalars
    assert sorted(tuple(sorted(edge)) for edge in join_tree.graph.edges()) == [
        (0, 1),
        (1, 2),
        (1, 3),
        (3, 4),
    ]
    assert sorted(tuple(sorted(edge)) for edge in split_tree.graph.edges()) == [
        (0, 2),
        (1, 2),
        (2, 4),
        (3, 4),
    ]
    assert sorted(tuple(sorted(edge)) for edge in contour_tree.graph.edges()) == [(3, 4)]
    assert [
        (pair.extremum, pair.saddle, pair.persistence, pair.kind)
        for pair in persistence_pairs
    ] == [
        (4, 3, 0.7, "join"),
        (1, 2, 0.39999999999999997, "split"),
        (2, 1, 0.39999999999999997, "join"),
    ]
    assert simplified_contour_tree is not None
    assert sorted(tuple(sorted(edge)) for edge in simplified_contour_tree.graph.edges()) == [
        (3, 4)
    ]


def test_path_graph_example_script_prints_walkthrough(capsys) -> None:
    module = load_path_graph_pipeline_module()

    module.main()

    output = capsys.readouterr().out
    assert "Input graph node scalars:" in output
    assert "Validated scalars:" in output
    assert "Ordered scalars:" in output
    assert "Join tree edges:" in output
    assert "Split tree edges:" in output
    assert "Contour tree edges:" in output
    assert "Persistence pairs:" in output
    assert "Simplified contour tree edges (threshold=0.5):" in output
