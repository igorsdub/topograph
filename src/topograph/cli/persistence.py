"""Persistence command implementations."""

import typer

app = typer.Typer()


@app.command()
def compute(input_file: str, output_file: str):
    """Compute persistence pairs from topological structure."""
    typer.echo(f"Computing persistence: {input_file} -> {output_file}")
