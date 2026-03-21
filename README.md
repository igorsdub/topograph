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

- Python + NetworkX only
- dataclass-based outputs
- deterministic tie handling
- modular functions that are easy to test

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
