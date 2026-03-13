"""Join tree command implementations."""

from pathlib import Path

import typer

from ._validation import load_and_validate_graph_or_exit

app = typer.Typer()


@app.command()
def compute(input_file: Path, output_file: Path):
    """Compute join tree from scalar field."""
    load_and_validate_graph_or_exit(input_file)

    typer.echo(f"Computing join tree: {input_file} -> {output_file}")
