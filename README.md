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

## Project Oragnization

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
│       │   ├── split_join.py
│       │   ├── contour_tree.py
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

I1 --> J[Compute persistence]

J --> J1([Contour tree<br/>persistence])

J1 --> K[Simplify]
I1 --> K

K --> L1([Simplified<br/>contour tree])
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

## Perturbation Module

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

## Tree CLI (Join/Split)

Use the staged tree commands to compute join and split trees:

```bash
topographer tree join data/input.pkl data/join_tree.pkl
topographer tree split data/input.pkl data/split_tree.pkl
topographer augment join data/input.pkl data/join_tree_aug.pkl
topographer augment split data/input.pkl data/split_tree_aug.pkl
```

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
