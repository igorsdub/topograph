"""Top-level Typer application for Topographer CLI commands."""

from pathlib import Path

import typer

from topographer.io.convert import convert_graph
from topographer.workflows import (
    create_pipeline_figures,
    run_medium_example_pipeline,
    save_pipeline_figures,
)

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
    """Convert a graph file between supported serialization formats."""
    convert_graph(
        source_path=source_path,
        target_path=target_path,
        source_format=source_format,
        target_format=target_format,
    )
    typer.echo(f"Converted graph: {source_path} -> {target_path}")


@app.command()
def example(
    output_dir: Path = typer.Option(
        Path("examples/output/medium_workflow"),
        "--output-dir",
        help="Directory where workflow figures will be saved.",
    ),
    threshold: float = typer.Option(
        4.0,
        "--threshold",
        help="Persistence simplification threshold.",
    ),
    format: str = typer.Option(
        "svg",
        "--format",
        help="Figure format: png, pdf, svg, html.",
    ),
    with_labels: bool = typer.Option(
        True,
        "--with-labels/--no-labels",
        help="Whether to annotate node labels on tree plots.",
    ),
) -> None:
    """Run the built-in medium end-to-end contour workflow example."""
    artifacts = run_medium_example_pipeline(simplification_threshold=threshold)
    figures = create_pipeline_figures(artifacts, with_labels=with_labels)
    output_paths = save_pipeline_figures(figures, output_dir=output_dir, format=format)

    typer.echo("Ran medium workflow example")
    typer.echo(f"Output directory: {output_dir}")
    for name, path in sorted(output_paths.items()):
        typer.echo(f"  - {name}: {path}")
