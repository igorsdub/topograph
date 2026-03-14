from __future__ import annotations

"""Persistence pair computation from contour-tree structure."""

from collections.abc import Hashable

from topographer.algorithms.contour_tree import compute_contour_tree_from_split_join
from topographer.models.persistence import PersistencePair, PersistenceResult
from topographer.models.tree import ContourTree, MergeTree


def _scalar_for_node(CT: ContourTree, node: Hashable) -> float:
    """Read scalar metadata for a contour-tree node as ``float``."""
    metadata = CT.node_metadata.get(node)
    if metadata is None or CT.scalar not in metadata:
        raise ValueError(f"Missing scalar metadata for contour tree node: {node!r}")

    return float(metadata[CT.scalar])


def _pairs_from_contour_tree(CT: ContourTree) -> list[PersistencePair]:
    """Build persistence pairs from contour-tree edges.

    Each contour-tree edge contributes one pair where birth/death are assigned
    by scalar ordering and persistence is the scalar difference magnitude.
    """
    pairs: list[PersistencePair] = []

    for a, b in CT.graph.edges():
        scalar_a = _scalar_for_node(CT, a)
        scalar_b = _scalar_for_node(CT, b)

        if scalar_a <= scalar_b:
            birth, death = a, b
            birth_scalar, death_scalar = scalar_a, scalar_b
        else:
            birth, death = b, a
            birth_scalar, death_scalar = scalar_b, scalar_a

        pairs.append(
            PersistencePair(
                birth=birth,
                death=death,
                birth_scalar=birth_scalar,
                death_scalar=death_scalar,
                persistence=abs(death_scalar - birth_scalar),
            )
        )

    pairs.sort(key=lambda pair: pair.persistence, reverse=True)
    return pairs


def compute_persistence_from_split_join(
    ST: MergeTree,
    JT: MergeTree,
) -> PersistenceResult:
    """Compute persistence by first building a contour tree from split/join trees."""
    if ST.scalar != JT.scalar:
        raise ValueError("Split tree and join tree must use the same scalar attribute")

    CT = compute_contour_tree_from_split_join(ST, JT)
    return PersistenceResult(scalar=CT.scalar, pairs=_pairs_from_contour_tree(CT))


def compute_persistence_from_contour_tree(CT: ContourTree) -> PersistenceResult:
    """Compute persistence directly from a contour tree with split/join context."""
    if CT.split_tree is None or CT.join_tree is None:
        raise ValueError(
            "Computing persistence from contour tree requires both split_tree and join_tree context"
        )

    return PersistenceResult(scalar=CT.scalar, pairs=_pairs_from_contour_tree(CT))


__all__ = [
    "compute_persistence_from_split_join",
    "compute_persistence_from_contour_tree",
]
