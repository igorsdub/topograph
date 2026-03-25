# Changelog

All notable changes to this project are documented in this file.

## Unreleased

### Added

* Created the minimal `src/topographer` package with:
  `__init__.py`, `api.py`, `core.py`, `trees.py`, `persistence.py`,
  `simplify.py`, `plot.py`, and `models.py`
* Implemented the end-to-end `run_pipeline(G, scalar, simplify_threshold=None)` API
* Added dataclass models for `MergeTree`, `ContourTree`, `PersistencePair`, and `PipelineResult`
* Added focused deterministic test modules for core validation, tree construction,
  persistence, simplification, plotting helpers, and pipeline execution
* Added a runnable example in `examples/basic_pipeline.py`
* Added compatibility helper APIs: `has_unique_scalars`, `make_total_ordering`,
  `compute_contour_tree_from_trees`, `compute_persistence`, and
  `simplify_tree_by_persistence`
* Added a rendered gallery workflow to `examples/basic_pipeline.py` that writes
  PNG stages, an `index.html`, and a `summary.json` for the full pipeline
* Added contract tests for the basic pipeline gallery metadata and simplified
  persistence semantics

### Changed

* Implemented graph validation, deterministic scalar ordering, and a simple `UnionFind`
* Implemented split tree and join tree sweeps using a simple filtration-style approach
* Implemented contour tree construction by merging split and join trees and contracting degree-2 nodes
* Implemented persistence pair computation from merge and contour trees
* Implemented threshold-based contour-tree simplification
* Simplified module boundaries so tree and persistence code rely on shared package
  models and core helpers instead of local fallback structures
* Expanded top-level exports and README usage examples to make the package easier
  to discover from `import topographer`
* Rewrote `README.md` to describe the minimal package and current development workflow
* Simplified `pixi.toml` and `pyproject.toml` to match the minimal NetworkX-based package
* Tightened the build configuration so the built artifact contains only the minimal package
* Recomputed simplified persistence diagrams from the simplified contour graph
  instead of reusing the original join/split trees
* Added `matplotlib` to the example/runtime environment for rendered gallery output

### Removed

* Removed legacy scaffold behavior from the built package artifact
* Removed stale generated artifacts and rebuilt the Pixi environment from a clean state

### Verified

* `pixi install`
* `pixi run python -m pytest -q`
* `pixi build`

Latest verification result:

* Test suite passed: `24 passed`
* Pixi build completed successfully
