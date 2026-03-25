"""Render a simple gallery for the basic Topographer pipeline."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import networkx as nx

from topographer import (
    compute_persistence,
    run_pipeline,
    save_graph_plot,
    save_persistence_diagram,
    save_tree_plot,
    write_gallery_html,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / "output" / "pipeline_plots"
DEFAULT_SCALAR = "height"
DEFAULT_SIMPLIFY_THRESHOLD = 1.5


@dataclass(frozen=True)
class StageSpec:
    key: str
    title: str
    filename: str


STAGES: tuple[StageSpec, ...] = (
    StageSpec("initial_graph", "Initial Graph", "01_initial_graph.png"),
    StageSpec("split_tree", "Split Tree", "02_split_tree.png"),
    StageSpec("join_tree", "Join Tree", "03_join_tree.png"),
    StageSpec("contour_tree", "Contour Tree", "04_contour_tree.png"),
    StageSpec("persistence_diagram", "Persistence Diagram", "05_persistence_diagram.png"),
    StageSpec(
        "simplified_persistence_diagram",
        "Simplified Persistence Diagram",
        "06_simplified_persistence_diagram.png",
    ),
    StageSpec("simplified_contour_tree", "Simplified Contour Tree", "07_simplified_contour_tree.png"),
)


def build_graph() -> nx.Graph:
    """Create the tiny deterministic graph used by the example."""

    graph = nx.Graph()
    graph.add_edges_from([(0, 1), (0, 2), (0, 3)])
    nx.set_node_attributes(graph, {0: 0.0, 1: 3.0, 2: 1.0, 3: 2.0}, DEFAULT_SCALAR)
    return graph


def _sorted_edges(graph: nx.Graph) -> list[tuple[Any, Any]]:
    return sorted(tuple(sorted(edge)) for edge in graph.edges())


def _pair_summary(graph: nx.Graph, pairs: list[Any]) -> list[dict[str, Any]]:
    return [
        {
            "extremum": pair.extremum,
            "extremum_scalar": float(graph.nodes[pair.extremum][DEFAULT_SCALAR]),
            "saddle": pair.saddle,
            "saddle_scalar": float(graph.nodes[pair.saddle][DEFAULT_SCALAR]),
            "persistence": float(pair.persistence),
            "kind": pair.kind,
        }
        for pair in pairs
    ]


def build_gallery_manifest(output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, Any]:
    """Build the stage metadata and summary for the example."""

    graph = build_graph()
    result = run_pipeline(
        graph,
        scalar=DEFAULT_SCALAR,
        simplify_threshold=DEFAULT_SIMPLIFY_THRESHOLD,
    )
    if result.simplified_contour_tree is None:
        raise RuntimeError("The example requires a simplified contour tree.")

    simplified_pairs = compute_persistence(result.simplified_contour_tree, scalar=DEFAULT_SCALAR)
    summary = {
        "scalar": DEFAULT_SCALAR,
        "simplify_threshold": DEFAULT_SIMPLIFY_THRESHOLD,
        "files": [stage.filename for stage in STAGES],
        "stages": [{"key": stage.key, "title": stage.title, "filename": stage.filename} for stage in STAGES],
        "graph_edges": _sorted_edges(graph),
        "split_tree_edges": _sorted_edges(result.split_tree.graph),
        "join_tree_edges": _sorted_edges(result.join_tree.graph),
        "contour_tree_edges": _sorted_edges(result.contour_tree.graph),
        "simplified_contour_tree_edges": _sorted_edges(result.simplified_contour_tree.graph),
        "persistence_pairs": _pair_summary(graph, result.persistence_pairs),
        "simplified_persistence_pairs": _pair_summary(result.simplified_contour_tree.graph, simplified_pairs),
    }
    return {
        "output_dir": output_dir,
        "result": result,
        "simplified_persistence_pairs": simplified_pairs,
        "summary": summary,
    }


def build_gallery(output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, Any]:
    """Render the gallery images, index, and summary JSON."""

    gallery = build_gallery_manifest(output_dir)
    result = gallery["result"]
    simplified_pairs = gallery["simplified_persistence_pairs"]
    summary = gallery["summary"]

    output_dir.mkdir(parents=True, exist_ok=True)

    save_graph_plot(
        result.input_graph,
        output_dir / STAGES[0].filename,
        scalar=DEFAULT_SCALAR,
        title=STAGES[0].title,
    )
    save_tree_plot(
        result.split_tree,
        output_dir / STAGES[1].filename,
        title=STAGES[1].title,
        node_color="#8a4d2d",
    )
    save_tree_plot(
        result.join_tree,
        output_dir / STAGES[2].filename,
        title=STAGES[2].title,
        node_color="#356f89",
    )
    save_tree_plot(
        result.contour_tree,
        output_dir / STAGES[3].filename,
        title=STAGES[3].title,
        edge_color="#9b5b36",
    )
    save_persistence_diagram(
        result.persistence_pairs,
        output_dir / STAGES[4].filename,
        graph=result.input_graph,
        scalar=DEFAULT_SCALAR,
        title=STAGES[4].title,
    )
    save_persistence_diagram(
        simplified_pairs,
        output_dir / STAGES[5].filename,
        graph=result.simplified_contour_tree.graph,
        scalar=DEFAULT_SCALAR,
        title=STAGES[5].title,
        point_color="#b55d33",
    )
    save_tree_plot(
        result.simplified_contour_tree,
        output_dir / STAGES[6].filename,
        title=STAGES[6].title,
        node_color="#8a4d2d",
        edge_color="#9b5b36",
    )

    write_gallery_html(summary["stages"], output_dir / "index.html")
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render the basic Topographer pipeline gallery.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for the generated PNGs, HTML index, and summary JSON.",
    )
    return parser.parse_args()


def main() -> None:
    """Generate the gallery and report the written files."""

    args = parse_args()
    summary = build_gallery(args.output_dir)
    print(f"Wrote pipeline gallery to {args.output_dir}")
    print("Generated files:", ", ".join(summary["files"]))


if __name__ == "__main__":
    main()
