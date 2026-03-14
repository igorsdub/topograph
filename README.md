# TopoGrapher

<a target="_blank" href="https://cookiecutter-data-science.drivendata.org/">
    <img src="https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter" />
</a>
<a target="_blank" href="https://pixi.prefix.dev/">
    <img src="https://img.shields.io/badge/pixi-Environment%20Manager-3776AB?logo=python" />
</a>
<a target="_blank" href="https://typer.tiangolo.com/">
    <img src="https://img.shields.io/badge/Typer-CLI%20Framework-009485" />
</a>

Topological analysis on graphs and networks.

## Project Organization

### Structure

```text
├── .gitignore
├── docs/                       <- Quarto documentation project
│   ├── _quarto.yml
│   ├── index.qmd               <- Documentation homepage
│   ├── api.qmd                 <- API reference
│   ├── cli.qmd                 <- CLI documentation
│   ├── theory/                 <- Theoretical background
│   │   ├── split_join_trees.qmd
│   │   ├── contour_tree.qmd
│   │   └── persistence.qmd
│   └── examples/               <- Tutorial examples
│       ├── path_graph.qmd
│       └── branching_graph.qmd
├── examples/                   <- Example scripts and data
│   ├── example_scalar_graph.py
│   └── example_cli.sh
├── src/
│   └── topographer/              <- Main package source code
│       ├── __init__.py
│       ├── cli.py              <- Command-line interface
│       ├── exceptions.py        <- Custom exceptions
│       ├── pipeline.py          <- Main pipeline orchestration
│       ├── algorithms/          <- Core topological algorithms
│       │   ├── __init__.py
│       │   ├── split_tree.py
│       │   ├── join_tree.py
│       │   ├── contour_tree.py
│       │   ├── persistence.py
│       │   └── simplification.py
│       ├── core/               <- Core utilities and data structures
│       │   ├── __init__.py
│       │   ├── validation.py
│       │   ├── ordering.py
│       │   ├── filtration.py
│       │   └── unionfind.py
│       ├── models/             <- Data models and structures
│       │   ├── __init__.py
│       │   ├── tree.py
│       │   └── persistence.py
│       ├── io/                 <- Input/output handlers
│       │   ├── __init__.py
│       │   ├── graphml.py
│       │   └── json.py
│       ├── transforms/         <- Graph transformations
│       │   ├── __init__.py
│       │   └── perturb.py
│       └── workflows/          <- High-level workflows
│           ├── __init__.py
│           └── contour_pipeline.py
├── tests/                      <- Unit and integration tests
│   ├── test_split_join.py
│   ├── test_contour_tree.py
│   ├── test_simplify.py
│   └── test_cli.py
├── LICENSE                     <- Open-source license
├── Makefile                    <- Convenience commands
├── README.md                   <- This file
├── pyproject.toml              <- Project configuration and dependencies
└── pixi.toml                   <- Pixi environment configuration
```

### Workflow

```mermaid
---
config:
  look: handDrawn
  theme: neutral
---
flowchart TD

A([Graph G<br/>w/ scalar f]) --> B[Validate graph and<br/>scalar attribute]

B --> C{Unique scalar values?}

C -->|Yes| F
C -->|No| D[ Break scalar ties]

D --> F([Graph G<br/>w/ scalar f'])

F --> G[Compute split/join tree]

G --> G1([Split tree])
G --> H1([Join tree])


G1 --> I[Compute contour tree]
H1 --> I

I --> I1([Contour tree])

I1 --> J[Compute<br/>persistence]

J --> J1([Contour tree<br/>persistence])

I1 --> K[Simplify]

K --> L1([Simplified<br/>contour tree])

I1 --> M[Visualize / Export]
```

## CLI Convert Example

Use `topographer convert` to convert graph files between `pkl`, `graphml`, `gml`, `gexf`, and `json`.

Show command help:

```bash
topographer convert --help
```

Convert between formats:

```bash
topographer convert data/source.pkl data/converted.json
topographer convert data/source.graphml data/converted.gml --source-format graphml --target-format gml
```

## Breaking Ties

Use `topographer.transforms.perturb` to deterministically break tied scalar values
without changing graph topology.

Main API:

- `has_ties(G, scalar)`
- `find_ties(G, scalar)`
- `perturb_ties(G, scalar, ...)`
- `is_strictly_ordered(G, scalar)`

CLI usage:

```bash
topographer perturb data/input.pkl data/output.pkl
topographer perturb data/input.pkl data/output.pkl --scalar scalar --output-scalar scalar_perturbed
```

The command writes a new graph file with tied groups perturbed in a deterministic
lexicographic order.

## Trees

Use staged commands to compute base trees first, then run augmentation as a
separate step:

```bash
topographer tree join data/input.pkl data/join_tree.pkl
topographer tree split data/input.pkl data/split_tree.pkl
topographer tree contour data/input.pkl data/contour_tree.pkl

topographer augment join data/input.pkl data/join_tree_aug.pkl
topographer augment split data/input.pkl data/split_tree_aug.pkl
topographer augment contour data/input.pkl data/contour_tree_aug.pkl
```

Contour tree construction does not perform augmentation automatically.
Use `topographer augment contour ...` when you need the augmented contour tree.

API usage follows the same staged pattern:

```python
from topographer import compute_contour_tree, augment_contour_tree

CT = compute_contour_tree(graph, scalar="scalar")
aCT = augment_contour_tree(CT)
```

`CT` is a rich wrapper object with graph topology plus split/join merge-tree context:

- `CT.graph`: contour tree topology (`nx.Graph`)
- `CT.JT` / `CT.join_tree`: join-oriented `MergeTree` (`kind == "join"`)
- `CT.ST` / `CT.split_tree`: split-oriented `MergeTree` (`kind == "split"`)
- `CT.scalar`: scalar attribute name

## Planar Tree Layout

Tree plotting layout is available for graphs with scalar node values:

- `planar_layout(tree, ...)` computes node coordinates
- `assign_planar_layout(tree, ...)` computes coordinates and writes them to node attributes

CLI usage:

```bash
topographer tree layout data/tree.pkl data/tree_layout.pkl
topographer tree layout data/tree.pkl data/tree_layout.pkl --scalar scalar --x-mode leaf_span
topographer tree layout data/tree.pkl data/tree_layout.pkl --root 0 --x-attr x --y-attr y --pos-attr pos
```

API usage:

```python
from topographer import assign_planar_layout, draw_tree, planar_layout, save_figure

pos = planar_layout(tree, scalar="scalar")
assign_planar_layout(tree, scalar="scalar", x_attr="layout_x", y_attr="layout_y")

fig, ax = draw_tree(tree, pos=pos, with_labels=True)
save_figure(fig, "tree_plot.svg")
```

## Tree Plot Export

Render a tree directly from CLI and save to image/HTML:

```bash
topographer tree plot data/tree.pkl data/tree.png
topographer tree plot data/tree.pkl data/tree.pdf
topographer tree plot data/tree.pkl data/tree.svg --with-labels
topographer tree plot data/tree.pkl data/tree.html --show-regular
```

Supported save formats are inferred from output extension: `png`, `pdf`, `svg`, `html`.

Useful options:

- `--scalar` to select the scalar attribute used for vertical placement
- `--root` to force a root node for layout
- `--x-mode leaf_span` for branch-based horizontal placement
- `--with-labels` to annotate node ids
- `--show-regular` to include regular (non-critical) nodes

## Persistence

Persistence is available via two explicit paths:

- split/join merge trees first, then persistence
- contour tree wrapper, then persistence

CLI usage:

```bash
topographer persistence compute data/input.pkl data/persistence_split_join.json --mode split-join
topographer persistence compute data/input.pkl data/persistence_contour.json --mode contour
```

API usage:

```python
from topographer.algorithms.contour_tree import compute_contour_tree
from topographer.algorithms.join_tree import compute_join_tree
from topographer.algorithms.persistence import (
    compute_persistence_from_contour_tree,
    compute_persistence_from_split_join,
)
from topographer.algorithms.split_tree import compute_split_tree

split_tree = compute_split_tree(graph, scalar="scalar")
join_tree = compute_join_tree(graph, scalar="scalar")
pairs_split_join = compute_persistence_from_split_join(split_tree, join_tree)

CT = compute_contour_tree(graph, scalar="scalar")
pairs_contour = compute_persistence_from_contour_tree(CT)
```

## Simplification

Simplification mirrors TTK-style orchestration:

- simplify join-oriented `MergeTree` context with a persistence threshold
- simplify split-oriented `MergeTree` context with the same threshold
- recompute `CT` from the simplified split/join merge-tree context

CLI usage:

```bash
topographer simplify threshold data/input.pkl data/contour_simplified.pkl --epsilon 0.5
topographer simplify threshold data/input.pkl data/contour_simplified.pkl --epsilon 1.0 --scalar scalar
```

API usage:

```python
from topographer.algorithms.contour_tree import compute_contour_tree
from topographer.algorithms.simplification import simplify_contour_tree

CT = compute_contour_tree(graph, scalar="scalar")
CT_simplified = simplify_contour_tree(CT, threshold=0.5)
```

## Example

Run the end-to-end medium example (graph checks, scalar tie handling,
split/join tree, contour tree, persistence, simplification, and visualization)
from the command line:

```bash
topographer example
```

If you are using Pixi:

```bash
pixi run topographer example
```

The script prints a stage summary and writes figures to:

- `examples/output/medium_workflow/original_graph.svg`
- `examples/output/medium_workflow/split_tree.svg`
- `examples/output/medium_workflow/join_tree.svg`
- `examples/output/medium_workflow/contour_tree.svg`
- `examples/output/medium_workflow/contour_tree_simplified.svg`
- `examples/output/medium_workflow/persistence_diagram.svg`
- `examples/output/medium_workflow/persistence_diagram_simplified.svg`

For package/API usage, see:

- `topographer.workflows.run_medium_example_pipeline`
- `topographer.workflows.create_pipeline_figures`
- `topographer.plotting.plot_persistence_diagram`

# References

## Package Building

- <https://pixi.prefix.dev/latest/build/python/>
- <https://packaging.python.org/>
- <https://typer.tiangolo.com/tutorial/package/>
- <https://typer.tiangolo.com/tutorial/one-file-per-command/>

## Topology

- <https://topology-tool-kit.github.io/>
- <https://github.com/maljovec/topopy>

## Graphs and Networks

- <https://networkx.org/en/>
