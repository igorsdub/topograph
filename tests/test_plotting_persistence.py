from __future__ import annotations

from pathlib import Path

import pytest

from topographer.models.persistence import PersistencePair, PersistenceResult
from topographer.plotting import plot_persistence_diagram, save_figure


def _sample_result() -> PersistenceResult:
    return PersistenceResult(
        scalar="scalar",
        pairs=[
            PersistencePair(
                birth="a",
                death="b",
                birth_scalar=0.5,
                death_scalar=1.0,
                persistence=0.5,
            ),
            PersistencePair(
                birth="c",
                death="d",
                birth_scalar=1.0,
                death_scalar=2.25,
                persistence=1.25,
            ),
        ],
    )


def test_plot_persistence_diagram_and_save_svg(tmp_path: Path) -> None:
    matplotlib = pytest.importorskip("matplotlib")
    matplotlib.use("Agg")
    pytest.importorskip("matplotlib.pyplot")

    fig, _ = plot_persistence_diagram(_sample_result(), with_diagonal=True, annotate=True)
    output = tmp_path / "persistence.svg"
    save_figure(fig, output)

    assert output.exists()


def test_plot_persistence_diagram_handles_empty_pairs(tmp_path: Path) -> None:
    matplotlib = pytest.importorskip("matplotlib")
    matplotlib.use("Agg")
    pytest.importorskip("matplotlib.pyplot")

    empty = PersistenceResult(scalar="scalar", pairs=[])
    fig, _ = plot_persistence_diagram(empty)

    output = tmp_path / "empty_diagram.html"
    save_figure(fig, output)

    assert output.exists()
    assert "<svg" in output.read_text(encoding="utf-8")
