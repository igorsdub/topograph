# Changelog

All notable changes to this project are documented in this file.

## Unreleased

### Added

* Created the minimal `src/topographer` package with:
  `__init__.py`, `api.py`, `core.py`, `trees.py`, `persistence.py`,
  `simplify.py`, `plot.py`, and `models.py`
* Implemented the end-to-end `run_pipeline(G, scalar, simplify_threshold=None)` API
* Added dataclass models for `MergeTree`, `ContourTree`, `PersistencePair`, and `PipelineResult`
* Added deterministic tests in `tests/test_pipeline.py`

### Changed

* Implemented graph validation, deterministic scalar ordering, and a simple `UnionFind`
* Implemented split tree and join tree sweeps using a simple filtration-style approach
* Implemented contour tree construction by merging split and join trees and contracting degree-2 nodes
* Implemented persistence pair computation from merge and contour trees
* Implemented threshold-based contour-tree simplification
* Rewrote `README.md` to describe the minimal package and current development workflow
* Simplified `pixi.toml` and `pyproject.toml` to match the minimal NetworkX-based package
* Tightened the build configuration so the built artifact contains only the minimal package

### Removed

* Removed legacy scaffold behavior from the built package artifact
* Removed stale generated artifacts and rebuilt the Pixi environment from a clean state

### Verified

* `pixi install`
* `pixi run python -m pytest -q`
* `pixi build`

Latest verification result:

* Test suite passed: `6 passed`
* Pixi build completed successfully
