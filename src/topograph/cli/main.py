"""Main CLI entry point."""

import typer

from ..transforms import app as transforms_app
from ..version import app as version_app
from . import (
    contour_tree,
    join_tree,
    persistence,
    run,
    simplify,
    split_tree,
)

app = typer.Typer()

# Add main app commands
app.add_typer(transforms_app, name="transforms")
app.add_typer(version_app)

# Add algorithm-specific subcommands
app.add_typer(split_tree.app, name="split-tree")
app.add_typer(join_tree.app, name="join-tree")
app.add_typer(contour_tree.app, name="contour-tree")
app.add_typer(persistence.app, name="persistence")
app.add_typer(simplify.app, name="simplify")

# Add run subcommand
app.add_typer(run.app, name="run")
