import networkx as nx
import pytest

from topograph.examples import (
    easy_path_graph,
    invalid_disconnected_graph,
    invalid_duplicate_scalar_graph,
    invalid_missing_scalar_graph,
)
from topograph.core.graph_check import check_graph


def test_check_graph_accepts_valid_connected_graph_with_numeric_scalars():
    G = easy_path_graph(3)
    assert check_graph(G) is True


def test_check_graph_rejects_non_networkx_graph():
    with pytest.raises(TypeError, match="Graph must be a networkx.Graph"):
        check_graph({})


def test_check_graph_rejects_empty_graph():
    G = nx.Graph()
    with pytest.raises(ValueError, match="Graph is empty"):
        check_graph(G)


def test_check_graph_rejects_disconnected_graph_when_required():
    G = invalid_disconnected_graph()

    with pytest.raises(ValueError, match="Graph must be connected"):
        check_graph(G, require_connected=True)


def test_check_graph_allows_disconnected_graph_when_not_required():
    G = invalid_disconnected_graph()

    assert check_graph(G, require_connected=False) is True


def test_check_graph_rejects_missing_scalar_attribute():
    G = invalid_missing_scalar_graph()

    with pytest.raises(ValueError, match="missing scalar attribute"):
        check_graph(G)


def test_check_graph_rejects_non_numeric_scalar_values():
    G = easy_path_graph(2)
    G.nodes[1]["scalar"] = "high"

    with pytest.raises(ValueError, match="must be numeric"):
        check_graph(G)


def test_check_graph_rejects_duplicate_scalar_values():
    G = invalid_duplicate_scalar_graph()

    with pytest.raises(ValueError, match="Duplicate scalar values detected"):
        check_graph(G)
