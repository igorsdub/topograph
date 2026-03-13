"""I/O command implementations."""

from pathlib import Path

import typer

from topographer.io.convert import convert_graph
from topographer.io.load import load_graph
from topographer.io.save import save_graph

app = typer.Typer()


@app.command()
def load(
    input_path: Path,
    file_format: str | None = typer.Option(
        None,
        "--format",
        help="Input graph format. If omitted, inferred from input extension.",
    ),
) -> None:
    """Load a graph and print a short summary."""
    graph = load_graph(input_path, file_format=file_format)
    typer.echo(
        f"Loaded graph from {input_path}: nodes={graph.number_of_nodes()} edges={graph.number_of_edges()}"
    )


@app.command()
def save(
    input_path: Path,
    output_path: Path,
    input_format: str | None = typer.Option(
        None,
        "--input-format",
        help="Input graph format. If omitted, inferred from input extension.",
    ),
    output_format: str | None = typer.Option(
        None,
        "--output-format",
        help="Output graph format. If omitted, inferred from output extension.",
    ),
) -> None:
    """Load a graph and save it to another path."""
    graph = load_graph(input_path, file_format=input_format)
    save_graph(graph, output_path, file_format=output_format)
    typer.echo(f"Saved graph to {output_path}")


@app.command()
def convert(
    source_path: Path,
    target_path: Path,
    source_format: str | None = typer.Option(
        None,
        "--source-format",
        help="Source graph format. If omitted, inferred from source extension.",
    ),
    target_format: str | None = typer.Option(
        None,
        "--target-format",
        help="Target graph format. If omitted, inferred from target extension.",
    ),
) -> None:
    """Convert a graph between supported formats."""
    convert_graph(
        source_path=source_path,
        target_path=target_path,
        source_format=source_format,
        target_format=target_format,
    )
    typer.echo(f"Converted graph: {source_path} -> {target_path}")
