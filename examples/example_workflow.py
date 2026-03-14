from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


def main() -> None:
    from topographer.core.uniqueness import are_scalar_values_unique
    from topographer.workflows import (
        create_pipeline_figures,
        run_medium_example_pipeline,
        save_pipeline_figures,
    )

    artifacts = run_medium_example_pipeline(simplification_threshold=4.0)

    print("=== Topographer medium workflow ===")
    print(f"Raw graph nodes: {artifacts.raw_graph.number_of_nodes()}")
    print(f"Raw graph edges: {artifacts.raw_graph.number_of_edges()}")

    was_unique_before = are_scalar_values_unique(artifacts.raw_graph, scalar_attr=artifacts.scalar)
    is_unique_after = are_scalar_values_unique(artifacts.graph, scalar_attr=artifacts.scalar)
    print(f"Unique scalar before perturbation: {was_unique_before}")
    print(f"Unique scalar after perturbation: {is_unique_after}")

    if artifacts.perturbation is not None:
        print(
            "Perturbed nodes:",
            len(artifacts.perturbation.perturbed_nodes),
            "(epsilon=",
            artifacts.perturbation.epsilon,
            ")",
        )

    print(f"Split tree nodes: {artifacts.split_tree.graph.number_of_nodes()}")
    print(f"Join tree nodes: {artifacts.join_tree.graph.number_of_nodes()}")
    print(f"Contour tree nodes: {artifacts.contour_tree.graph.number_of_nodes()}")
    print(f"Persistence pairs: {len(artifacts.persistence.pairs)}")
    print(
        "Simplified contour tree nodes:",
        artifacts.simplified_contour_tree.graph.number_of_nodes(),
    )

    figures = create_pipeline_figures(artifacts, with_labels=True)
    output_paths = save_pipeline_figures(
        figures,
        output_dir=PROJECT_ROOT / "examples" / "output" / "medium_workflow",
        format="svg",
    )

    print("Saved figures:")
    for name, path in sorted(output_paths.items()):
        print(f"  - {name}: {path}")


if __name__ == "__main__":
    main()
