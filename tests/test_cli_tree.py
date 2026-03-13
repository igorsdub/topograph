import pickle

from typer.testing import CliRunner

from topographer.cli.main import app
from topographer.examples import easy_path_graph, invalid_missing_scalar_graph
from topographer.io.load import load_graph

runner = CliRunner()


def _write_graph(path, graph) -> None:
    with path.open("wb") as handle:
        pickle.dump(graph, handle)


def test_tree_join_command_writes_output_graph(tmp_path):
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
    source_path = tmp_path / "invalid.pkl"
    output_path = tmp_path / "join.pkl"

    _write_graph(source_path, invalid_missing_scalar_graph())

    result = runner.invoke(app, ["tree", "join", str(source_path), str(output_path)])

    assert result.exit_code == 1
    assert "missing scalar attribute" in result.stdout
