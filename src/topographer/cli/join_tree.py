"""CLI commands for join-tree computation."""

from pathlib import Path

import typer

from ._validation import load_and_validate_graph_or_exit

app = typer.Typer()


@app.command()
def compute(
    input_file: Path,
    output_file: Path,
    scalar: str = typer.Option("scalar", "--scalar", help="Scalar attribute name."),
):
    """Compute a join tree from the input scalar graph and write it to disk."""
    load_and_validate_graph_or_exit(input_file, scalar_attr=scalar)

    typer.echo(f"Computing join tree: {input_file} -> {output_file}")
