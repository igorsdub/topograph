"""Main CLI entry point."""

from pathlib import Path

import typer

from topographer.io.convert import convert_graph

from ..version import app as version_app
from . import (
    augment,
    contour_tree,
    join_tree,
    persistence,
    perturb,
    run,
    simplify,
    split_tree,
    tree,
)

app = typer.Typer()

app.add_typer(version_app)

# Add algorithm-specific subcommands
app.add_typer(split_tree.app, name="split-tree")
app.add_typer(join_tree.app, name="join-tree")
app.add_typer(contour_tree.app, name="contour-tree")
app.add_typer(persistence.app, name="persistence")
app.add_typer(simplify.app, name="simplify")
app.add_typer(perturb.app, name="perturb")
app.add_typer(tree.app, name="tree")
app.add_typer(augment.app, name="augment")

# Add run subcommand
app.add_typer(run.app, name="run")


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
