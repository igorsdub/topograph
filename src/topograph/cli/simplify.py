"""Simplification command implementations."""

import typer

app = typer.Typer()


@app.command()
def threshold(
    input_file: str,
    output_file: str,
    epsilon: float = typer.Option(..., help="Simplification threshold"),
):
    """Simplify topological structure using persistence threshold."""
    typer.echo(
        f"Simplifying with epsilon={epsilon}: {input_file} -> {output_file}"
    )
