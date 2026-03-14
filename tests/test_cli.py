import json
import pickle

import networkx as nx
import pytest
from typer.testing import CliRunner

from topographer.cli.main import app
from topographer.examples import (
    easy_path_graph,
    invalid_duplicate_scalar_graph,
    invalid_missing_scalar_graph,
)
from topographer.io.load import load_graph
from topographer.transforms.perturb import is_strictly_ordered

runner = CliRunner()


def _write_pickle_graph(path, graph: nx.Graph) -> None:
    """Serialize a graph to pickle for CLI file-based test inputs."""
    with path.open("wb") as handle:
        pickle.dump(graph, handle)


def test_convert_command_converts_graph(tmp_path):
    """Verify the top-level convert command rewrites a graph to target format."""
    source_path = tmp_path / "source.pkl"
    target_path = tmp_path / "converted.gexf"
    _write_pickle_graph(source_path, easy_path_graph(2))

    result = runner.invoke(app, ["convert", str(source_path), str(target_path)])

    assert result.exit_code == 0
    assert target_path.exists()
    assert "Converted graph" in result.stdout

    loaded = load_graph(target_path)
    assert loaded.number_of_nodes() == 2
    assert loaded.number_of_edges() == 1


def _write_graph(path, graph: nx.Graph) -> None:
    """Write a graph to pickle for command tests that expect input files."""
    with path.open("wb") as handle:
        pickle.dump(graph, handle)


def test_split_tree_compute_rejects_missing_scalar(tmp_path):
    """Ensure split-tree CLI fails fast when required scalar attributes are missing."""
    source_path = tmp_path / "invalid.pkl"
    output_path = tmp_path / "split_tree.pkl"

    graph = invalid_missing_scalar_graph()

    _write_graph(source_path, graph)

    result = runner.invoke(
        app,
        ["split-tree", "compute", str(source_path), str(output_path)],
    )

    assert result.exit_code == 1
    assert "missing scalar attribute" in result.stdout


def test_run_pipeline_validates_graph_before_execution(tmp_path):
    """Confirm pipeline command validates a valid graph and starts execution."""
    source_path = tmp_path / "valid.pkl"
    output_path = tmp_path / "output.pkl"

    graph = easy_path_graph(2)

    _write_graph(source_path, graph)

    result = runner.invoke(
        app,
        ["run", "pipeline", str(source_path), str(output_path)],
    )

    assert result.exit_code == 0
    assert "Running pipeline" in result.stdout


def test_perturb_ties_cli_writes_perturbed_scalar(tmp_path):
    """Check perturb command writes an output graph with strict perturbed ordering."""
    source_path = tmp_path / "tied.pkl"
    output_path = tmp_path / "perturbed.pkl"

    graph = invalid_duplicate_scalar_graph()
    _write_graph(source_path, graph)

    result = runner.invoke(
        app,
        ["perturb", str(source_path), str(output_path)],
    )

    assert result.exit_code == 0
    assert "Perturbed scalar ties" in result.stdout

    loaded = load_graph(output_path)
    assert is_strictly_ordered(loaded, "scalar_perturbed")


def test_perturb_ties_cli_rejects_missing_scalar_attribute(tmp_path):
    """Ensure perturb command reports a clear error for missing scalar input."""
    source_path = tmp_path / "missing_scalar.pkl"
    output_path = tmp_path / "perturbed.pkl"

    graph = invalid_missing_scalar_graph()
    _write_graph(source_path, graph)

    result = runner.invoke(
        app,
        ["perturb", str(source_path), str(output_path)],
    )

    assert result.exit_code == 1
    assert "Missing scalar attribute" in result.stdout


def test_persistence_compute_split_join_mode_writes_pairs(tmp_path):
    """Verify persistence command in split-join mode emits expected JSON payload."""
    source_path = tmp_path / "input.pkl"
    output_path = tmp_path / "persistence_split_join.json"

    graph = easy_path_graph(6)
    _write_graph(source_path, graph)

    result = runner.invoke(
        app,
        [
            "persistence",
            "compute",
            str(source_path),
            str(output_path),
            "--mode",
            "split-join",
        ],
    )

    assert result.exit_code == 0
    assert output_path.exists()
    assert "Computed persistence" in result.stdout

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["mode"] == "split-join"
    assert payload["scalar"] == "scalar"
    assert len(payload["pairs"]) == 1
    assert payload["pairs"][0]["persistence"] == 5.0


def test_persistence_compute_contour_mode_writes_pairs(tmp_path):
    """Verify persistence command in contour mode emits expected JSON payload."""
    source_path = tmp_path / "input.pkl"
    output_path = tmp_path / "persistence_contour.json"

    graph = easy_path_graph(6)
    _write_graph(source_path, graph)

    result = runner.invoke(
        app,
        [
            "persistence",
            "compute",
            str(source_path),
            str(output_path),
            "--mode",
            "contour",
        ],
    )

    assert result.exit_code == 0
    assert output_path.exists()
    assert "Computed persistence" in result.stdout

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["mode"] == "contour"
    assert payload["scalar"] == "scalar"
    assert len(payload["pairs"]) == 1
    assert payload["pairs"][0]["persistence"] == 5.0


def test_simplify_threshold_command_writes_simplified_contour_tree(tmp_path):
    """Check simplify threshold command writes a non-empty simplified contour tree."""
    source_path = tmp_path / "input.pkl"
    output_path = tmp_path / "simplified.pkl"

    graph = easy_path_graph(6)
    _write_graph(source_path, graph)

    result = runner.invoke(
        app,
        [
            "simplify",
            "threshold",
            str(source_path),
            str(output_path),
            "--epsilon",
            "0.5",
        ],
    )

    assert result.exit_code == 0
    assert output_path.exists()
    assert "Simplified contour tree" in result.stdout

    out_graph = load_graph(output_path)
    assert out_graph.number_of_nodes() > 0
    assert out_graph.number_of_edges() > 0


def test_example_command_runs_medium_workflow_and_writes_figures(tmp_path):
    """Ensure top-level example command runs and saves all expected workflow plots."""
    matplotlib = pytest.importorskip("matplotlib")
    matplotlib.use("Agg")

    output_dir = tmp_path / "medium_workflow"

    result = runner.invoke(
        app,
        [
            "example",
            "--output-dir",
            str(output_dir),
            "--format",
            "svg",
        ],
    )

    assert result.exit_code == 0
    assert "Ran medium workflow example" in result.stdout

    expected = {
        "original_graph.svg",
        "split_tree.svg",
        "join_tree.svg",
        "contour_tree.svg",
        "contour_tree_simplified.svg",
        "persistence_diagram.svg",
        "persistence_diagram_simplified.svg",
    }

    produced = {path.name for path in output_dir.glob("*.svg")}
    assert expected.issubset(produced)
