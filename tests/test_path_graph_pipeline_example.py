"""Tests for runnable example pipeline scripts."""

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

SCRIPT_TO_BUILDER = {
    "path_graph_pipeline": "make_path_graph",
    "trivial_graph_pipeline": "make_trivial_graph",
    "circular_graph_pipeline": "make_circular_graph",
    "star_graph_pipeline": "make_star_graph",
    "tadpole_graph_pipeline": "make_tadpole_graph",
    "wheel_graph_pipeline": "make_wheel_graph",
    "cubical_graph_pipeline": "make_cubical_graph",
    "windmill_graph_pipeline": "make_windmill_graph",
    "cave_man_graph_pipeline": "make_cave_man_graph",
    "ladder_graph_pipeline": "make_ladder_graph",
    "balanced_tree_graph_pipeline": "make_balanced_tree_graph",
}

REQUIRED_HEADINGS = [
    "Input graph node scalars:",
    "Validated scalars:",
    "Ordered scalars:",
    "Join tree edges:",
    "Split tree edges:",
    "Contour tree edges:",
    "Contour tree persistence pairs:",
    "Wrote SVG plots:",
    "Simplified contour tree persistence pairs:",
]


def load_example_module(script_name: str):
    """Load the example module from its file path."""

    root = Path(__file__).resolve().parents[1]
    module_path = root / "examples" / f"{script_name}.py"
    spec = importlib.util.spec_from_file_location(f"{script_name}_example", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load examples/{script_name}.py")

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_example_pipeline_script_set_matches_builder_exports() -> None:
    example_dir = Path(__file__).resolve().parents[1] / "examples"
    script_names = {
        path.stem
        for path in example_dir.glob("*_graph_pipeline.py")
    }
    script_names.add("path_graph_pipeline")

    assert script_names == set(SCRIPT_TO_BUILDER)


def test_example_pipeline_scripts_load_and_write_svg_plots(tmp_path: Path, capsys) -> None:
    for script_name in SCRIPT_TO_BUILDER:
        module = load_example_module(script_name)
        output_dir = tmp_path / script_name

        module.main(output_dir=output_dir)

        output = capsys.readouterr().out
        for heading in REQUIRED_HEADINGS:
            assert heading in output
        assert "Simplified contour tree edges (threshold=0.5):" in output

        assert (output_dir / "01_original_graph.svg").exists()
        assert (output_dir / "02_split_tree.svg").exists()
        assert (output_dir / "03_join_tree.svg").exists()
        assert (output_dir / "04_contour_tree.svg").exists()
        assert (output_dir / "05_contour_tree_persistence.svg").exists()
        assert (output_dir / "06_simplified_contour_tree.svg").exists()
        assert (output_dir / "07_simplified_contour_tree_persistence.svg").exists()


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
    simplified_persistence_pairs = compute_persistence(
        simplified_contour_tree,
        scalar="scalar",
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
    assert contour_tree.graph.number_of_nodes() == graph.number_of_nodes()
    assert contour_tree.graph.number_of_edges() == graph.number_of_nodes() - 1
    assert sorted(tuple(sorted(edge)) for edge in contour_tree.graph.edges()) == [
        (0, 1),
        (1, 2),
        (1, 3),
        (3, 4),
    ]
    assert {
        node: (join_tree.graph.nodes[node]["node_type"], join_tree.graph.nodes[node]["saddle_type"])
        for node in join_tree.graph.nodes
    } == {
        0: ("min", None),
        1: ("sad", "join_sad"),
        2: ("min", None),
        3: ("max", None),
        4: ("min", None),
    }
    assert {
        node: (split_tree.graph.nodes[node]["node_type"], split_tree.graph.nodes[node]["saddle_type"])
        for node in split_tree.graph.nodes
    } == {
        0: ("min", None),
        1: ("max", None),
        2: ("sad", "split_sad"),
        3: ("max", None),
        4: ("reg", None),
    }
    assert {
        node: (contour_tree.graph.nodes[node]["node_type"], contour_tree.graph.nodes[node]["saddle_type"])
        for node in contour_tree.graph.nodes
    } == {
        0: ("min", None),
        1: ("max", None),
        2: ("min", None),
        3: ("max", None),
        4: ("min", None),
    }
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
        (0, 1),
        (1, 3),
        (3, 4),
    ]
    assert [
        (pair.extremum, pair.saddle, pair.persistence, pair.kind)
        for pair in simplified_persistence_pairs
    ] == [(4, 3, 0.7, "join")]


def test_path_graph_example_script_prints_walkthrough(capsys) -> None:
    module = load_example_module("path_graph_pipeline")

    module.main()

    output = capsys.readouterr().out
    for heading in REQUIRED_HEADINGS:
        assert heading in output
    assert "Simplified contour tree edges (threshold=0.5):" in output


def test_path_graph_example_script_writes_svg_plots(tmp_path: Path) -> None:
    module = load_example_module("path_graph_pipeline")

    module.main(output_dir=tmp_path)

    assert (tmp_path / "01_original_graph.svg").exists()
    assert (tmp_path / "02_split_tree.svg").exists()
    assert (tmp_path / "03_join_tree.svg").exists()
    assert (tmp_path / "04_contour_tree.svg").exists()
    assert (tmp_path / "05_contour_tree_persistence.svg").exists()
    assert (tmp_path / "06_simplified_contour_tree.svg").exists()
    assert (tmp_path / "07_simplified_contour_tree_persistence.svg").exists()
