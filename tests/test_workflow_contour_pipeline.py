from __future__ import annotations

import pytest

from topographer.core.uniqueness import are_scalar_values_unique
from topographer.workflows import (
    create_pipeline_figures,
    medium_example_graph,
    run_contour_pipeline,
    run_medium_example_pipeline,
)


def test_medium_example_graph_contains_non_unique_scalars() -> None:
    graph = medium_example_graph()
    assert are_scalar_values_unique(graph, scalar_attr="scalar") is False


def test_run_contour_pipeline_breaks_ties_and_runs_all_stages() -> None:
    artifacts = run_contour_pipeline(
        medium_example_graph(),
        simplification_threshold=1.5,
    )

    assert artifacts.perturbation is not None
    assert artifacts.perturbation.ties_found is True
    assert are_scalar_values_unique(artifacts.graph, scalar_attr=artifacts.scalar) is True

    assert artifacts.split_tree.kind == "split"
    assert artifacts.join_tree.kind == "join"
    assert artifacts.contour_tree.split_tree is not None
    assert artifacts.contour_tree.join_tree is not None
    assert len(artifacts.persistence.pairs) > 0
    assert len(artifacts.simplified_persistence.pairs) >= 0


def test_create_pipeline_figures_returns_expected_keys() -> None:
    matplotlib = pytest.importorskip("matplotlib")
    matplotlib.use("Agg")
    pytest.importorskip("matplotlib.pyplot")

    artifacts = run_medium_example_pipeline(simplification_threshold=1.5)
    figures = create_pipeline_figures(artifacts, with_labels=False)

    assert set(figures) == {
        "original_graph",
        "split_tree",
        "join_tree",
        "contour_tree",
        "contour_tree_simplified",
        "persistence_diagram",
        "persistence_diagram_simplified",
    }

    contour_axes = figures["contour_tree"].axes
    assert contour_axes
    assert contour_axes[0].get_ylabel() == "scalar value"
