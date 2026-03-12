"""Split tree command implementations."""

import typer

app = typer.Typer()


@app.command()
def compute(input_file: str, output_file: str):
    """Compute split tree from scalar field."""
    typer.echo(f"Computing split tree: {input_file} -> {output_file}")
