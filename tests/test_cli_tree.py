import pickle

import networkx as nx
from typer.testing import CliRunner

from topographer.cli.main import app
from topographer.examples import easy_path_graph, invalid_missing_scalar_graph
from topographer.io.load import load_graph

runner = CliRunner()


def _write_graph(path, graph) -> None:
    """Persist a graph fixture to disk for CLI invocation tests."""
    with path.open("wb") as handle:
        pickle.dump(graph, handle)


def test_tree_join_command_writes_output_graph(tmp_path):
    """Ensure grouped tree join command writes a valid non-empty output graph."""
    source_path = tmp_path / "input.pkl"
    output_path = tmp_path / "join.pkl"

    _write_graph(source_path, easy_path_graph(6))

    result = runner.invoke(app, ["tree", "join", str(source_path), str(output_path)])

    assert result.exit_code == 0
    assert output_path.exists()
    assert "Computed join tree" in result.stdout

    out_graph = load_graph(output_path)
    assert out_graph.number_of_nodes() > 0
    assert out_graph.number_of_edges() > 0


def test_augment_split_command_writes_augmented_tree(tmp_path):
    """Verify augment split command preserves path-graph size after augmentation."""
    source_path = tmp_path / "input.pkl"
    output_path = tmp_path / "split_aug.pkl"

    input_graph = easy_path_graph(6)
    _write_graph(source_path, input_graph)

    result = runner.invoke(
        app,
        ["augment", "split", str(source_path), str(output_path)],
    )

    assert result.exit_code == 0
    assert output_path.exists()

    out_graph = load_graph(output_path)
    assert out_graph.number_of_nodes() == input_graph.number_of_nodes()
    assert out_graph.number_of_edges() == input_graph.number_of_edges()


def test_augment_join_command_writes_augmented_tree(tmp_path):
    """Verify augment join command preserves path-graph size after augmentation."""
    source_path = tmp_path / "input.pkl"
    output_path = tmp_path / "join_aug.pkl"

    input_graph = easy_path_graph(6)
    _write_graph(source_path, input_graph)

    result = runner.invoke(
        app,
        ["augment", "join", str(source_path), str(output_path)],
    )

    assert result.exit_code == 0
    assert output_path.exists()

    out_graph = load_graph(output_path)
    assert out_graph.number_of_nodes() == input_graph.number_of_nodes()
    assert out_graph.number_of_edges() == input_graph.number_of_edges()


def test_tree_join_rejects_missing_scalar_attribute(tmp_path):
    """Check tree join command returns validation error for missing scalar data."""
    source_path = tmp_path / "invalid.pkl"
    output_path = tmp_path / "join.pkl"

    _write_graph(source_path, invalid_missing_scalar_graph())

    result = runner.invoke(app, ["tree", "join", str(source_path), str(output_path)])

    assert result.exit_code == 1
    assert "missing scalar attribute" in result.stdout


def test_contour_tree_compute_command_writes_output_graph(tmp_path):
    """Ensure contour-tree compute command writes a non-empty output graph."""
    source_path = tmp_path / "input.pkl"
    output_path = tmp_path / "contour.pkl"

    _write_graph(source_path, easy_path_graph(6))

    result = runner.invoke(
        app,
        ["contour-tree", "compute", str(source_path), str(output_path)],
    )

    assert result.exit_code == 0
    assert output_path.exists()
    assert "Computed contour tree" in result.stdout

    out_graph = load_graph(output_path)
    assert out_graph.number_of_nodes() > 0
    assert out_graph.number_of_edges() > 0


def test_contour_tree_compute_rejects_augmentation_option(tmp_path):
    """Confirm unsupported contour-tree CLI options are rejected by Typer parsing."""
    source_path = tmp_path / "input.pkl"
    output_path = tmp_path / "contour.pkl"

    _write_graph(source_path, easy_path_graph(6))

    result = runner.invoke(
        app,
        [
            "contour-tree",
            "compute",
            str(source_path),
            str(output_path),
            "--augment",
        ],
    )

    assert result.exit_code != 0
    assert "No such option" in result.output


def test_augment_contour_command_writes_augmented_tree(tmp_path):
    """Verify augment contour command preserves size and reports completion."""
    source_path = tmp_path / "input.pkl"
    output_path = tmp_path / "contour_aug.pkl"

    input_graph = easy_path_graph(6)
    _write_graph(source_path, input_graph)

    result = runner.invoke(
        app,
        ["augment", "contour", str(source_path), str(output_path)],
    )

    assert result.exit_code == 0
    assert output_path.exists()
    assert "Computed augmented contour tree" in result.stdout

    out_graph = load_graph(output_path)
    assert out_graph.number_of_nodes() == input_graph.number_of_nodes()
    assert out_graph.number_of_edges() == input_graph.number_of_edges()


def test_tree_layout_command_writes_layout_attributes(tmp_path):
    """Ensure tree layout command computes and saves planar node coordinates."""
    source_path = tmp_path / "tree.pkl"
    output_path = tmp_path / "tree_layout.pkl"

    input_graph = easy_path_graph(6)
    _write_graph(source_path, input_graph)

    result = runner.invoke(
        app,
        ["tree", "layout", str(source_path), str(output_path)],
    )

    assert result.exit_code == 0
    assert output_path.exists()
    assert "Computed tree layout" in result.stdout

    out_graph = load_graph(output_path)
    for node in out_graph.nodes:
        assert "layout_x" in out_graph.nodes[node]
        assert "layout_y" in out_graph.nodes[node]
        assert "pos" in out_graph.nodes[node]


def test_tree_layout_command_rejects_non_tree_graph(tmp_path):
    """Check tree layout command fails clearly when graph is not a tree."""
    source_path = tmp_path / "cycle.pkl"
    output_path = tmp_path / "cycle_layout.pkl"

    graph = nx.cycle_graph(4)
    for node in graph.nodes:
        graph.nodes[node]["scalar"] = float(node)

    _write_graph(source_path, graph)

    result = runner.invoke(
        app,
        ["tree", "layout", str(source_path), str(output_path)],
    )

    assert result.exit_code == 1
    assert "connected acyclic graph" in result.stdout
