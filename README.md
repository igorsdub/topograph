# TopoGrapher

Minimal topological analysis for scalar graphs built on NetworkX.

## Overview

`topographer` implements a small, inspectable pipeline for computing:

- split tree
- join tree
- contour tree
- persistence pairs
- persistence-based simplification

The package is intentionally simple:

- Python + NetworkX core algorithms
- dataclass-based outputs
- deterministic tie handling
- modular functions that are easy to test
- lightweight plotting-data helpers for graphs, trees, and persistence pairs
- a runnable path-graph walkthrough example

## Package Layout

```text
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

## Pipeline

The main entry point is `run_pipeline`:

1. Validate the graph and scalar attribute
2. Enforce a total scalar order
3. Compute join tree
4. Compute split tree
5. Merge them into a contour tree
6. Compute persistence pairs
7. Optionally simplify low-persistence arcs

Lower-level helpers are also available:

- `check_graph`, `has_unique_scalars`, `make_total_ordering`
- `compute_join_tree`, `compute_split_tree`, `compute_contour_tree`
- `compute_contour_tree_from_trees`
- `compute_persistence`
- `simplify_tree_by_persistence`
- `plot_graph`, `plot_tree`, `plot_persistence_diagram`

## Example

```python
import networkx as nx

from topographer import run_pipeline

G = nx.path_graph(5)
nx.set_node_attributes(
    G,
    {0: 0.0, 1: 2.0, 2: 1.0, 3: 3.0, 4: 4.0},
    "height",
)

result = run_pipeline(G, scalar="height", simplify_threshold=1.5)

print("Join tree edges:", list(result.join_tree.graph.edges()))
print("Split tree edges:", list(result.split_tree.graph.edges()))
print(
    "Persistence pairs:",
    [(pair.extremum, pair.saddle, pair.persistence) for pair in result.persistence_pairs],
)
```

A standalone runnable example is available in
[`examples/path_graph_pipeline.py`](examples/path_graph_pipeline.py).
Run it with:

```bash
pixi run python examples/path_graph_pipeline.py
```

It prints each pipeline step in order for a small path graph and writes SVG plots for:

- original node scalars
- validated and ordered scalars
- the original graph, split tree, join tree, and contour tree
- persistence pairs
- simplified contour tree edges

## Development

Install the Pixi environment:

```bash
pixi install
```

Run tests:

```bash
pixi run python -m pytest -q
```

Build the package:

```bash
pixi build
```
