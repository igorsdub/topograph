"""Split/join tree model aliases for compatibility and convenience."""

from topographer.models.tree import (
    JoinTree,
    JoinTreeResult,
    MergeTree,
    MergeTreeResult,
    SplitTree,
    SplitTreeResult,
)

__all__ = [
    "MergeTree",
    "SplitTree",
    "JoinTree",
    "MergeTreeResult",
    "SplitTreeResult",
    "JoinTreeResult",
]
