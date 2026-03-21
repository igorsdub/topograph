"""Basic end-to-end example for the topographer pipeline."""

from __future__ import annotations

import networkx as nx

from topographer import run_pipeline


def main() -> None:
    """Run the minimal contour-tree pipeline on a tiny graph."""

    graph = nx.Graph()
    graph.add_edges_from([(0, 1), (0, 2), (0, 3)])
    nx.set_node_attributes(graph, {0: 0.0, 1: 3.0, 2: 1.0, 3: 2.0}, "height")

    result = run_pipeline(graph, scalar="height", simplify_threshold=1.5)

    print("join edges:", sorted(result.join_tree.graph.edges()))
    print("split edges:", sorted(result.split_tree.graph.edges()))
    print(
        "pairs:",
        [(pair.extremum, pair.saddle, pair.persistence) for pair in result.persistence_pairs],
    )


if __name__ == "__main__":
    main()
