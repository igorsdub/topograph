# AGENTS.md

## Purpose

This repository implements a **minimal, extensible topology toolkit for graphs** based on scalar functions on nodes.

Core goals:

* Compute **split tree**, **join tree**, and **contour tree**
* Compute **persistence pairs**
* Perform **simplification based on persistence**
* Provide a **clear, inspectable pipeline**
* Stay **simple, readable, and modifiable**

This is **not a performance-focused implementation**. Clarity and correctness come first.

---

## Core Mental Model

The entire library follows a **fixed pipeline**:

[
G \rightarrow \text{validate} \rightarrow \text{ordering}
\rightarrow (T_s, T_j)
\rightarrow T_c
\rightarrow P
\rightarrow T_c^{simp}
]

Where:

* (G): input graph with scalar field
* (T_s): split tree
* (T_j): join tree
* (T_c): contour tree
* (P): persistence pairs

Agents MUST preserve this structure.

---

## Package Structure

```
src/topographer/
├── __init__.py
├── api.py
├── core.py
├── trees.py
├── persistence.py
├── simplify.py
├── plot.py
└── models.py
```

### Responsibilities

* **core.py**

  * validation
  * scalar ordering
  * union-find

* **trees.py**

  * split tree
  * join tree
  * contour tree

* **persistence.py**

  * persistence pair computation

* **simplify.py**

  * tree simplification

* **models.py**

  * dataclasses only

* **api.py**

  * pipeline orchestration

* **plot.py**

  * lightweight plotting data helpers only

---

## Non-Negotiable Design Rules

### 1. Keep It Simple

* No unnecessary abstractions
* No premature optimization
* Prefer explicit code over clever code

### 2. Determinism

* All algorithms must be deterministic
* Tie-breaking must be stable

### 3. No Hidden State

* No globals
* No implicit mutation unless clearly documented

### 4. Type Safety

* Use type hints everywhere
* Use dataclasses for structured outputs

### 5. NetworkX Is the Ground Truth

* Graphs are always `nx.Graph`
* Scalar values are node attributes

---

## Algorithmic Constraints

### Sweep Logic (CRITICAL)

* Join tree → **ascending order**
* Split tree → **descending order**
* Use **Union-Find** for component tracking

Agents MUST follow this paradigm.

---

## Models

All structured data MUST live in `models.py`.

Required:

* `MergeTree`
* `ContourTree`
* `PersistencePair`
* `PipelineResult`

Rules:

* Keep models lightweight
* No heavy logic inside models

---

## Pipeline (api.py)

The main entry point:

```python
run_pipeline(G, scalar="scalar", simplify_threshold=None)
```

This must:

1. Validate graph
2. Ensure scalar ordering
3. Compute join tree
4. Compute split tree
5. Compute contour tree
6. Compute persistence
7. Optionally simplify
8. Return `PipelineResult`

Do NOT bypass steps.

---

## Testing (pytest REQUIRED)

All functionality must be testable.

Minimum tests:

* graph validation
* scalar handling
* tree construction sanity
* persistence computation
* pipeline execution

Tests must:

* use small graphs
* be deterministic
* avoid randomness unless seeded
* continue to pass with `pixi run python -m pytest -q`

---

## What NOT to Do

Agents must NOT:

* Introduce deep class hierarchies
* Add unnecessary dependencies
* Mix plotting with algorithms
* Optimize prematurely
* Rewrite structure into subpackages (yet)
* Implement full TTK complexity
* Reintroduce legacy scaffold modules, CLI layers, or old subpackage layouts unless explicitly requested

---

## Acceptable Simplifications

For early versions:

* Persistence can be approximate but consistent
* Contour tree merging can be simplified
* Simplification can be basic threshold filtering

Clarity > completeness

---

## Extension Guidelines

When extending:

* Preserve pipeline order
* Add functionality **without breaking API**
* Prefer adding functions over modifying behavior
* Keep backward compatibility

---

## Style Guide

* Small functions
* Clear variable names
* Docstrings for public functions
* Comments where algorithmic intent matters

---

## Final Principle

> This code should be understandable in ~10 minutes by a human.

If an agent produces something that violates this, it is wrong.

After tasks complete update CHANGELOG.md
