"""CLI commands for persistence pair computation and export."""

from enum import Enum
import json
from pathlib import Path

import typer

from topographer.algorithms.contour_tree import compute_contour_tree
from topographer.algorithms.join_tree import compute_join_tree
from topographer.algorithms.persistence import (
    compute_persistence_from_contour_tree,
    compute_persistence_from_split_join,
)
from topographer.algorithms.split_tree import compute_split_tree

from ._validation import load_and_validate_graph_or_exit

app = typer.Typer()


class PersistenceMode(str, Enum):
    """Persistence computation strategy exposed via CLI."""

    split_join = "split-join"
    contour = "contour"


@app.command()
def compute(
    input_file: Path,
    output_file: Path,
    scalar: str = typer.Option("scalar", "--scalar", help="Scalar attribute name."),
    mode: PersistenceMode = typer.Option(
        PersistenceMode.split_join,
        "--mode",
        help="Persistence computation mode: split-join or contour.",
        case_sensitive=False,
    ),
):
    """Compute persistence pairs and write them as JSON output.

    The command supports two modes: building pairs from split/join merge trees
    or from a computed contour tree.
    """
    graph = load_and_validate_graph_or_exit(input_file, scalar_attr=scalar)

    if mode is PersistenceMode.split_join:
        split_tree = compute_split_tree(graph, scalar=scalar)
        join_tree = compute_join_tree(graph, scalar=scalar)
        result = compute_persistence_from_split_join(split_tree, join_tree)
    else:
        contour_tree = compute_contour_tree(graph, scalar=scalar)
        result = compute_persistence_from_contour_tree(contour_tree)

    payload = result.to_dict()
    payload["mode"] = mode.value
    output_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    typer.echo(f"Computed persistence: {input_file} -> {output_file}")
