from __future__ import annotations

"""Graph saving helpers for supported NetworkX serialization formats."""

import json
from pathlib import Path
import pickle
from typing import Literal

import networkx as nx

GraphFormat = Literal["pkl", "graphml", "gml", "gexf", "json"]


def _normalize_format(path: str | Path, file_format: str | None = None) -> GraphFormat:
    """Resolve and validate a graph file format.

    The format is inferred from the file suffix when ``file_format`` is not
    provided. ``pickle`` is normalized to ``pkl``.
    """

    if file_format is not None:
        normalized = file_format.strip().lower().lstrip(".")
    else:
        normalized = Path(path).suffix.lower().lstrip(".")

    if normalized == "pickle":
        normalized = "pkl"

    supported_formats = {"pkl", "graphml", "gml", "gexf", "json"}
    if normalized not in supported_formats:
        raise ValueError(f"Unsupported graph format: {normalized}")

    return normalized  # type: ignore[return-value]


def save_graph(graph: nx.Graph, path: str | Path, file_format: str | None = None) -> None:
    """Persist a NetworkX graph to disk.

    Supported formats: ``pkl``, ``graphml``, ``gml``, ``gexf``, and ``json``.
    When ``file_format`` is omitted, format is inferred from the file extension.
    """

    graph_path = Path(path)
    normalized_format = _normalize_format(graph_path, file_format=file_format)

    if normalized_format == "pkl":
        with graph_path.open("wb") as handle:
            pickle.dump(graph, handle)
        return

    if normalized_format == "graphml":
        nx.write_graphml(graph, graph_path)
        return

    if normalized_format == "gml":
        nx.write_gml(graph, graph_path)
        return

    if normalized_format == "gexf":
        nx.write_gexf(graph, graph_path)
        return

    with graph_path.open("w", encoding="utf-8") as handle:
        json.dump(nx.node_link_data(graph, edges="links"), handle)
