"""Simplification command implementations."""

from pathlib import Path

import typer

from ._validation import load_and_validate_graph_or_exit

app = typer.Typer()


@app.command()
def threshold(
    input_file: Path,
    output_file: Path,
    epsilon: float = typer.Option(..., help="Simplification threshold"),
):
    """Simplify topological structure using persistence threshold."""
    load_and_validate_graph_or_exit(input_file)

    typer.echo(f"Simplifying with epsilon={epsilon}: {input_file} -> {output_file}")
