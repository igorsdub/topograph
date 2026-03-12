"""Run command implementations."""

import typer

app = typer.Typer()


@app.command()
def pipeline(input_file: str, output_file: str):
    """Run the complete topographic analysis pipeline."""
    typer.echo(f"Running pipeline: {input_file} -> {output_file}")
