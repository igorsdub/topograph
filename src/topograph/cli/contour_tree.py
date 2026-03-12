"""Contour tree command implementations."""

import typer

app = typer.Typer()


@app.command()
def compute(input_file: str, output_file: str):
    """Compute contour tree from scalar field."""
    typer.echo(f"Computing contour tree: {input_file} -> {output_file}")
