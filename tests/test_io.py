import json
import pickle

import networkx as nx
import pytest

from topograph.examples import easy_path_graph
from topograph.io.convert import convert_graph
from topograph.io.load import load_graph
from topograph.io.save import save_graph


def _sample_graph() -> nx.Graph:
    graph = nx.relabel_nodes(easy_path_graph(3), {0: "a", 1: "b", 2: "c"})
    graph.graph["name"] = "sample"

    graph.nodes["a"]["value"] = 1
    graph.nodes["b"]["value"] = 2
    graph.nodes["c"]["value"] = 3

    graph.edges[("a", "b")]["weight"] = 1.5
    graph.edges[("b", "c")]["weight"] = 2.5

    return graph


def _assert_graph_equal(actual: nx.Graph, expected: nx.Graph) -> None:
    assert set(actual.nodes) == set(expected.nodes)
    assert set(actual.edges) == set(expected.edges)

    for node in expected.nodes:
        assert actual.nodes[node]["value"] == expected.nodes[node]["value"]

    for edge in expected.edges:
        assert actual.edges[edge]["weight"] == expected.edges[edge]["weight"]


def _write_with_networkx(graph: nx.Graph, path, file_format: str) -> None:
    if file_format == "pkl":
        with path.open("wb") as handle:
            pickle.dump(graph, handle)
        return

    if file_format == "graphml":
        nx.write_graphml(graph, path)
        return

    if file_format == "gml":
        nx.write_gml(graph, path)
        return

    if file_format == "gexf":
        nx.write_gexf(graph, path)
        return

    if file_format == "json":
        with path.open("w", encoding="utf-8") as handle:
            json.dump(nx.node_link_data(graph, edges="links"), handle)
        return

    raise AssertionError(f"Unsupported test format: {file_format}")


def _read_with_networkx(path, file_format: str) -> nx.Graph:
    if file_format == "pkl":
        with path.open("rb") as handle:
            return pickle.load(handle)

    if file_format == "graphml":
        return nx.read_graphml(path)

    if file_format == "gml":
        return nx.read_gml(path)

    if file_format == "gexf":
        return nx.read_gexf(path)

    if file_format == "json":
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        return nx.node_link_graph(payload, edges="links")

    raise AssertionError(f"Unsupported test format: {file_format}")


@pytest.mark.parametrize("file_format", ["pkl", "graphml", "gml", "gexf", "json"])
def test_load_graph_supported_formats(tmp_path, file_format: str):
    graph = _sample_graph()
    path = tmp_path / f"input.{file_format}"

    _write_with_networkx(graph, path, file_format)

    loaded = load_graph(path)

    _assert_graph_equal(loaded, graph)


@pytest.mark.parametrize("file_format", ["pkl", "graphml", "gml", "gexf", "json"])
def test_save_graph_supported_formats(tmp_path, file_format: str):
    graph = _sample_graph()
    path = tmp_path / f"output.{file_format}"

    save_graph(graph, path)

    loaded = _read_with_networkx(path, file_format)

    _assert_graph_equal(loaded, graph)


@pytest.mark.parametrize("target_format", ["pkl", "graphml", "gml", "gexf", "json"])
def test_convert_graph_supported_formats(tmp_path, target_format: str):
    source_graph = _sample_graph()
    source_path = tmp_path / "source.pkl"
    target_path = tmp_path / f"converted.{target_format}"

    _write_with_networkx(source_graph, source_path, "pkl")

    convert_graph(source_path, target_path)

    converted = _read_with_networkx(target_path, target_format)

    _assert_graph_equal(converted, source_graph)


def test_load_graph_unsupported_format_raises(tmp_path):
    path = tmp_path / "graph.txt"
    path.write_text("not a graph", encoding="utf-8")

    with pytest.raises(ValueError, match="Unsupported graph format"):
        load_graph(path)


def test_save_graph_unsupported_format_raises(tmp_path):
    path = tmp_path / "graph.txt"

    with pytest.raises(ValueError, match="Unsupported graph format"):
        save_graph(_sample_graph(), path)


def test_convert_graph_unsupported_format_raises(tmp_path):
    source_path = tmp_path / "source.pkl"
    target_path = tmp_path / "target.txt"

    _write_with_networkx(_sample_graph(), source_path, "pkl")

    with pytest.raises(ValueError, match="Unsupported graph format"):
        convert_graph(source_path, target_path)
