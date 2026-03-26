"""Step-by-step topological analysis for a windmill graph."""

from __future__ import annotations

from pathlib import Path
import sys

from topographer import make_windmill_graph

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parent))
    from _example_pipeline import run_example_pipeline
else:
    from ._example_pipeline import run_example_pipeline

SCALAR = "scalar"
SIMPLIFY_THRESHOLD = 0.5
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "output" / "windmill_graph_pipeline"


def main(output_dir: Path = OUTPUT_DIR) -> None:
    """Run the windmill-graph walkthrough."""

    run_example_pipeline(
        build_graph=make_windmill_graph,
        output_dir=output_dir,
        example_name="windmill graph",
        scalar=SCALAR,
        simplify_threshold=SIMPLIFY_THRESHOLD,
    )


if __name__ == "__main__":
    main()
