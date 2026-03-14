"""CLI commands for persistence-threshold simplification."""

from pathlib import Path

import typer

from topographer.algorithms.contour_tree import compute_contour_tree
from topographer.algorithms.simplification import simplify_contour_tree
from topographer.io.save import save_graph

from ._validation import load_and_validate_graph_or_exit

app = typer.Typer()


@app.command()
def threshold(
    input_file: Path,
    output_file: Path,
    epsilon: float = typer.Option(..., help="Simplification threshold"),
    scalar: str = typer.Option("scalar", "--scalar", help="Scalar attribute name."),
):
    """Simplify contour-tree context using a persistence threshold.

    The command computes contour-tree context from input graph, simplifies the
    join/split merge-tree context with ``epsilon``, then recomputes and saves
    the simplified contour tree.
    """
    graph = load_and_validate_graph_or_exit(input_file, scalar_attr=scalar)
    contour_tree = compute_contour_tree(graph, scalar=scalar)
    simplified = simplify_contour_tree(contour_tree, threshold=epsilon)
    save_graph(simplified.tree, output_file)

    typer.echo(f"Simplified contour tree with epsilon={epsilon}: {input_file} -> {output_file}")
