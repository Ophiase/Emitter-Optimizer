import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from itertools import pairwise
from pathlib import Path

ARROW = re.compile(r"<?(?:-->|---|-\.->|-\.-|==>|===|~~~)(?:\|[^|]*\|)?")
SHAPE = re.compile(
    r"""(\[\(|\(\[|\[\[|\(\(|\{\{|\[|\(|\{)("[^"]*"|[^\]\)\}"])*(\)\]|\]\)|\]\]|\)\)|\}\}|\]|\)|\})"""
)
NODE = re.compile(r"[A-Za-z0-9_]+")
SWEEPS = 6


@dataclass
class Graph:
    start_line: int
    nodes: list[str] = field(default_factory=list)
    groups: dict[str, str] = field(default_factory=dict)
    edges: list[tuple[str, str]] = field(default_factory=list)

    def declare(self, node: str, group: str | None) -> None:
        if node not in self.nodes:
            self.nodes.append(node)
            self.groups[node] = group or node

    def read(self, line: str, group: str | None) -> None:
        stripped = SHAPE.sub("", line.strip())
        parts = [part.strip() for part in ARROW.split(stripped)]
        names = [match.group(0) for part in parts if (match := NODE.match(part))]
        for name in names:
            self.declare(name, group)
        self.edges.extend(pairwise(names))


class Layout:
    """Ranks by longest path, then counts crossings between adjacent ranks.

    An edge spanning several ranks gets one dummy per rank it crosses, placed
    after the real nodes in declaration order, as a first layout would.
    """

    def __init__(self, graph: Graph) -> None:
        self.graph = graph
        self.rank = self._ranks()
        self.rows: dict[int, list[str]] = defaultdict(list)
        self.links: list[tuple[str, str]] = []
        for node in graph.nodes:
            self.rows[self.rank[node]].append(node)
        for index, (source, target) in enumerate(graph.edges):
            self._link(index, source, target)

    def _ranks(self) -> dict[str, int]:
        rank = dict.fromkeys(self.graph.nodes, 0)
        for _ in self.graph.nodes:
            for source, target in self.graph.edges:
                if rank[target] < rank[source] + 1 <= len(self.graph.nodes):
                    rank[target] = rank[source] + 1
        for _ in self.graph.nodes:
            for node in self.graph.nodes:
                self._pull_down(rank, node)
        return rank

    def _pull_down(self, rank: dict[str, int], node: str) -> None:
        """Lowers a node when that shortens more edges than it lengthens."""
        below = [rank[target] for source, target in self.graph.edges if source == node]
        above = [rank[source] for source, target in self.graph.edges if target == node]
        if not below or len(below) < len(above):
            return
        lowest = min(below) - 1
        if lowest > rank[node] and (not above or lowest > max(above)):
            rank[node] = lowest

    def _link(self, index: int, source: str, target: str) -> None:
        previous = source
        for row in range(self.rank[source] + 1, self.rank[target]):
            dummy = f"edge{index}@{row}"
            self.rows[row].append(dummy)
            self.graph.groups[dummy] = dummy
            self.links.append((previous, dummy))
            previous = dummy
        if self.rank[target] > self.rank[source]:
            self.links.append((previous, target))

    def crossings(self, rows: dict[int, list[str]]) -> int:
        position = {
            node: index for row in rows.values() for index, node in enumerate(row)
        }
        by_row: dict[int, list[tuple[int, int]]] = defaultdict(list)
        for source, target in self.links:
            by_row[self.rank_of(source)].append((position[source], position[target]))
        return sum(
            1
            for pairs in by_row.values()
            for first in range(len(pairs))
            for second in range(first + 1, len(pairs))
            if (pairs[first][0] - pairs[second][0])
            * (pairs[first][1] - pairs[second][1])
            < 0
        )

    def rank_of(self, node: str) -> int:
        return self.rank[node] if node in self.rank else int(node.rsplit("@", 1)[1])

    def best(self) -> dict[int, list[str]]:
        rows = {row: list(nodes) for row, nodes in self.rows.items()}
        best = {row: list(nodes) for row, nodes in rows.items()}
        for sweep in range(SWEEPS):
            order = sorted(rows) if sweep % 2 == 0 else sorted(rows, reverse=True)
            for row in order[1:]:
                rows[row] = self._sorted(rows, row, downward=sweep % 2 == 0)
            if self.crossings(rows) < self.crossings(best):
                best = {row: list(nodes) for row, nodes in rows.items()}
        return best

    def _sorted(
        self, rows: dict[int, list[str]], row: int, downward: bool
    ) -> list[str]:
        neighbour_row = row - 1 if downward else row + 1
        position = {
            node: index for index, node in enumerate(rows.get(neighbour_row, []))
        }
        weights: dict[str, float] = {}
        for index, node in enumerate(rows[row]):
            neighbours = [
                position[other]
                for source, target in self.links
                for mine, other in ((target, source), (source, target))
                if mine == node and other in position
            ]
            weights[node] = sum(neighbours) / len(neighbours) if neighbours else index
        group_weight: dict[str, list[float]] = defaultdict(list)
        for node in rows[row]:
            group_weight[self.graph.groups[node]].append(weights[node])
        return sorted(
            rows[row],
            key=lambda node: (
                sum(group_weight[self.graph.groups[node]])
                / len(group_weight[self.graph.groups[node]]),
                weights[node],
            ),
        )


def graphs(lines: list[str]) -> list[tuple[Graph, set[int]]]:
    found: list[tuple[Graph, set[int]]] = []
    graph: Graph | None = None
    groups: list[str] = []
    for number, line in enumerate(lines, start=1):
        text = line.strip()
        if text.startswith("```mermaid"):
            graph, groups = Graph(number), []
            found.append((graph, {number}))
            continue
        if graph is None:
            continue
        found[-1][1].add(number)
        if text.startswith("```"):
            graph = None
        elif text.startswith("subgraph "):
            groups.append(text.split()[1])
        elif text == "end":
            groups = groups[:-1]
        elif ARROW.search(text) or NODE.fullmatch(SHAPE.sub("", text) or "-"):
            graph.read(text, groups[-1] if groups else None)
    return found


def first_block(lines: list[str], start: int) -> bool:
    return lines[start].strip().split()[0:1] in (["graph"], ["flowchart"])


def report(path: str, added: str) -> None:
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    wanted = (
        None if added == "ALL" else {int(line) for line in added.split(",") if line}
    )
    for graph, block in graphs(lines):
        if wanted is not None and not block & wanted:
            continue
        if graph.start_line >= len(lines) or not first_block(lines, graph.start_line):
            continue
        layout = Layout(graph)
        now = layout.crossings(layout.rows)
        best_rows = layout.best()
        best = layout.crossings(best_rows)
        if best < now:
            order = ", ".join(
                node
                for row in sorted(best_rows)
                for node in best_rows[row]
                if "@" not in node
            )
            print(
                f"{path}:{graph.start_line}: [CROSSING] {now} crossing(s), {best} "
                f"in another order; declare the nodes as: {order}"
            )


if __name__ == "__main__":
    report(sys.argv[1], sys.argv[2])
