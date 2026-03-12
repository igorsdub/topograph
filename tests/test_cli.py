import pickle

import networkx as nx
from typer.testing import CliRunner

from topograph.cli.main import app
from topograph.examples import easy_path_graph, invalid_missing_scalar_graph
from topograph.io.load import load_graph

runner = CliRunner()


def _write_pickle_graph(path, graph: nx.Graph) -> None:
    with path.open("wb") as handle:
        pickle.dump(graph, handle)


def test_convert_command_converts_graph(tmp_path):
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
    with path.open("wb") as handle:
        pickle.dump(graph, handle)


def test_split_tree_compute_rejects_missing_scalar(tmp_path):
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
