from __future__ import annotations

from typing import Any

CONTOUR_STYLE: dict[str, dict[str, Any]] = {
    "minima": {"marker": "o", "node_size": 70, "node_color": "#1f77b4"},
    "maxima": {"marker": "^", "node_size": 70, "node_color": "#d62728"},
    "saddles": {"marker": "D", "node_size": 80, "node_color": "#ff7f0e"},
    "regular": {"marker": "o", "node_size": 20, "node_color": "#7f7f7f"},
    "edges": {"width": 1.2, "edge_color": "#4c4c4c", "alpha": 0.9},
    "labels": {"font_size": 8, "font_color": "#222222"},
}

SPLIT_STYLE = CONTOUR_STYLE
JOIN_STYLE = CONTOUR_STYLE

__all__ = ["CONTOUR_STYLE", "SPLIT_STYLE", "JOIN_STYLE"]
