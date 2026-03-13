from __future__ import annotations

"""Graph format conversion helpers built on top of load/save operations."""

from pathlib import Path

from topographer.io.load import load_graph
from topographer.io.save import save_graph


def convert_graph(
    source_path: str | Path,
    target_path: str | Path,
    source_format: str | None = None,
    target_format: str | None = None,
) -> None:
    """Convert a graph file between supported serialization formats.

    Source and target formats can be explicitly provided or inferred from the
    corresponding file extensions.
    """

    graph = load_graph(source_path, file_format=source_format)
    save_graph(graph, target_path, file_format=target_format)
