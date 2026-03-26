"""Lightweight data models for the topographer pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, TypeAlias

import networkx as nx

NodeType: TypeAlias = Literal["max", "min", "sad", "reg"]
SaddleType: TypeAlias = Literal["join_sad", "split_sad"]


@dataclass(slots=True)
class MergeTree:
    """A merge tree representation backed by a NetworkX graph.

    The graph stores the tree structure. Node and edge metadata are kept
    simple so the object stays easy to inspect and extend later.
    """

    graph: nx.Graph
    scalar: str
    kind: str = ""
    node_metadata: dict[Any, dict[str, Any]] = field(default_factory=dict)
    arc_metadata: dict[tuple[Any, Any], dict[str, Any]] = field(default_factory=dict)


@dataclass(slots=True)
class ContourTree:
    """A contour tree representation backed by a NetworkX graph."""

    graph: nx.Graph
    scalar: str
    join_tree: MergeTree | None = None
    split_tree: MergeTree | None = None
    node_metadata: dict[Any, dict[str, Any]] = field(default_factory=dict)
    arc_metadata: dict[tuple[Any, Any], dict[str, Any]] = field(default_factory=dict)


@dataclass(slots=True)
class PersistencePair:
    """A persistence pair linking two critical nodes."""

    extremum: Any
    saddle: Any
    persistence: float
    kind: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def birth(self) -> Any:
        """Alias for the extremum node."""

        return self.extremum

    @property
    def death(self) -> Any:
        """Alias for the saddle node."""

        return self.saddle

    @property
    def left(self) -> Any:
        """Alias for the extremum node."""

        return self.extremum

    @property
    def right(self) -> Any:
        """Alias for the saddle node."""

        return self.saddle


@dataclass(slots=True)
class PipelineResult:
    """Container for all outputs produced by the pipeline."""

    input_graph: nx.Graph
    scalar: str
    ordered_graph: nx.Graph
    ordered_scalar: dict[Any, float]
    split_tree: MergeTree
    join_tree: MergeTree
    contour_tree: ContourTree
    persistence_pairs: list[PersistencePair]
    simplified_contour_tree: ContourTree | None = None

    @property
    def graph(self) -> nx.Graph:
        """Alias for the original input graph."""

        return self.input_graph
