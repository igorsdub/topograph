from __future__ import annotations

"""Graph loading helpers for supported NetworkX serialization formats."""

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


def load_graph(path: str | Path, file_format: str | None = None) -> nx.Graph:
    """Load a NetworkX graph from disk.

    Supported formats: ``pkl``, ``graphml``, ``gml``, ``gexf``, and ``json``.
    When ``file_format`` is omitted, format is inferred from the file extension.
    """

    graph_path = Path(path)
    normalized_format = _normalize_format(graph_path, file_format=file_format)

    if normalized_format == "pkl":
        with graph_path.open("rb") as handle:
            return pickle.load(handle)

    if normalized_format == "graphml":
        return nx.read_graphml(graph_path)

    if normalized_format == "gml":
        return nx.read_gml(graph_path)

    if normalized_format == "gexf":
        return nx.read_gexf(graph_path)

    with graph_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return nx.node_link_graph(payload, edges="links")
