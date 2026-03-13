from __future__ import annotations

"""Shared CLI validation helpers."""

from pathlib import Path

import networkx as nx
import typer

from topographer.core.graph_check import check_graph
from topographer.io.load import load_graph


def load_and_validate_graph_or_exit(
    input_file: Path,
    scalar_attr: str = "scalar",
    require_connected: bool = True,
) -> nx.Graph:
    """Load a graph from disk and validate it for algorithm execution."""

    try:
        graph = load_graph(input_file)
        check_graph(
            graph,
            scalar_attr=scalar_attr,
            require_connected=require_connected,
        )
    except (TypeError, ValueError) as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=1) from exc

    return graph
