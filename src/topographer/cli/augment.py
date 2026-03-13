"""Augmentation command group for split and join trees."""

from pathlib import Path

import typer

from topographer.algorithms.augmentation import augment_join_tree, augment_split_tree
from topographer.algorithms.join_tree import compute_join_tree
from topographer.algorithms.split_tree import compute_split_tree
from topographer.io.save import save_graph

from ._validation import load_and_validate_graph_or_exit

app = typer.Typer()


@app.command("join")
def join(
    input_file: Path,
    output_file: Path,
    scalar: str = typer.Option("scalar", "--scalar", help="Scalar attribute name."),
):
    """Compute augmented join tree as a post-construction stage."""
    graph = load_and_validate_graph_or_exit(input_file, scalar_attr=scalar)
    base = compute_join_tree(graph, scalar=scalar)
    result = augment_join_tree(base)
    save_graph(result.tree, output_file)
    typer.echo(f"Computed augmented join tree: {input_file} -> {output_file}")


@app.command("split")
def split(
    input_file: Path,
    output_file: Path,
    scalar: str = typer.Option("scalar", "--scalar", help="Scalar attribute name."),
):
    """Compute augmented split tree as a post-construction stage."""
    graph = load_and_validate_graph_or_exit(input_file, scalar_attr=scalar)
    base = compute_split_tree(graph, scalar=scalar)
    result = augment_split_tree(base)
    save_graph(result.tree, output_file)
    typer.echo(f"Computed augmented split tree: {input_file} -> {output_file}")
