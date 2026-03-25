"""Tests for the basic pipeline gallery example."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

from topographer.api import run_pipeline


def load_basic_pipeline_module():
    """Load the example module from its file path."""

    root = Path(__file__).resolve().parents[1]
    module_path = root / "examples" / "basic_pipeline.py"
    spec = importlib.util.spec_from_file_location("basic_pipeline_example", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load examples/basic_pipeline.py")

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_gallery_manifest_uses_requested_stage_order() -> None:
    module = load_basic_pipeline_module()

    manifest = module.build_gallery_manifest(Path("output/test_gallery"))
    stage_titles = [stage["title"] for stage in manifest["summary"]["stages"]]

    assert stage_titles == [
        "Initial Graph",
        "Split Tree",
        "Join Tree",
        "Contour Tree",
        "Persistence Diagram",
        "Simplified Persistence Diagram",
        "Simplified Contour Tree",
    ]
    assert "Ordered Graph" not in stage_titles


def test_gallery_manifest_recomputes_simplified_persistence_from_simplified_tree() -> None:
    module = load_basic_pipeline_module()

    manifest = module.build_gallery_manifest(Path("output/test_gallery"))
    result = manifest["result"]
    threshold = manifest["summary"]["simplify_threshold"]

    assert result.simplified_contour_tree is not None
    assert manifest["simplified_persistence_pairs"] == []
    assert [
        pair.persistence
        for pair in result.persistence_pairs
        if pair.persistence >= threshold
    ] == [2.0]


def test_gallery_manifest_exposes_stage_payloads_and_summary_files() -> None:
    module = load_basic_pipeline_module()

    manifest = module.build_gallery_manifest(Path("output/test_gallery"))
    summary = manifest["summary"]

    assert summary["files"] == [
        "01_initial_graph.png",
        "02_split_tree.png",
        "03_join_tree.png",
        "04_contour_tree.png",
        "05_persistence_diagram.png",
        "06_simplified_persistence_diagram.png",
        "07_simplified_contour_tree.png",
    ]
    assert summary["simplified_persistence_pairs"] == []
    assert summary["persistence_pairs"] == [
        {
            "extremum": 3,
            "extremum_scalar": 2.0,
            "kind": "split",
            "persistence": 2.0,
            "saddle": 0,
            "saddle_scalar": 0.0,
        },
        {
            "extremum": 2,
            "extremum_scalar": 1.0,
            "kind": "split",
            "persistence": 1.0,
            "saddle": 0,
            "saddle_scalar": 0.0,
        },
    ]


def test_pipeline_still_returns_simplified_tree_for_gallery_graph() -> None:
    module = load_basic_pipeline_module()

    result = run_pipeline(
        module.build_graph(),
        scalar=module.DEFAULT_SCALAR,
        simplify_threshold=module.DEFAULT_SIMPLIFY_THRESHOLD,
    )

    assert result.simplified_contour_tree is not None
