from __future__ import annotations

"""Persistence diagram plotting helpers."""

from importlib import import_module
from typing import Any

from topographer.models.persistence import PersistenceResult


def plot_persistence_diagram(
    result: PersistenceResult,
    *,
    ax: Any | None = None,
    with_diagonal: bool = True,
    annotate: bool = False,
    title: str = "Persistence Diagram",
) -> tuple[Any, Any]:
    """Plot a persistence diagram from a ``PersistenceResult`` payload."""
    try:
        plt = import_module("matplotlib.pyplot")
    except Exception as exc:
        raise RuntimeError("matplotlib is required for persistence plotting") from exc

    if ax is None:
        fig, ax = plt.subplots(figsize=(6, 5), constrained_layout=True)
    else:
        fig = ax.figure

    births = [pair.birth_scalar for pair in result.pairs]
    deaths = [pair.death_scalar for pair in result.pairs]

    if births and deaths:
        ax.scatter(births, deaths, s=36, alpha=0.9)

        if with_diagonal:
            min_scalar = min(min(births), min(deaths))
            max_scalar = max(max(births), max(deaths))
            padding = max(1e-9, (max_scalar - min_scalar) * 0.05)
            lower = min_scalar - padding
            upper = max_scalar + padding
            ax.plot([lower, upper], [lower, upper], linestyle="--", linewidth=1.0, alpha=0.7)
            ax.set_xlim(lower, upper)
            ax.set_ylim(lower, upper)

        if annotate:
            for pair in result.pairs:
                label = f"({pair.birth},{pair.death})"
                ax.annotate(
                    label,
                    (pair.birth_scalar, pair.death_scalar),
                    textcoords="offset points",
                    xytext=(4, 4),
                    fontsize=8,
                )

    ax.set_xlabel("Birth")
    ax.set_ylabel("Death")
    ax.set_title(title)
    ax.grid(True, linestyle="--", linewidth=0.5, alpha=0.4)
    return fig, ax


__all__ = ["plot_persistence_diagram"]
