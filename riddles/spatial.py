import random
from collections import deque
from core import BaseRiddle, riddle

_NODE_POOL = [
    'VX-7',   'OBELISK', 'CAISSON',  'LUMEN',   'BRACKET',
    'SILT',   'FERRITE', 'NODULE',   'CIPHER',  'WELD',
    'BASALT', 'TROUGH',  'SPINDLE',  'FLANGE',  'CULVERT',
    'DATUM',  'MANTLE',  'HINGE',    'PELLET',  'SCORIA'
]

_RUMOURS = [
    'Unverified: {a} may connect directly to {b} (last sighting: unknown).',
    'Field report (disputed): a passage from {a} toward {b} was noted.',
    'Rumour only — do not rely: {a} → {b} found in old maintenance logs.'
]


def _gen_graph(rng, n=13):
    nodes = rng.sample(_NODE_POOL, n)
    graph = {nd: set() for nd in nodes}
    order = nodes[:]
    rng.shuffle(order)

    for i in range(len(order) - 1):
        graph[order[i]].add(order[i + 1])

    for nd in nodes:
        pool = [x for x in nodes if x != nd and x not in graph[nd]]

        rng.shuffle(pool)

        for t in pool[:rng.randint(1, 3)]:
            graph[nd].add(t)

    return nodes, {k: sorted(v) for k, v in graph.items()}

def _bfs(graph, src, dst, blocked):
    q, seen = deque([[src]]), {src}

    while q:
        path = q.popleft()
        node = path[-1]

        if node == dst:
            return path

        for nb in graph.get(node, []):
            if nb not in seen and nb not in blocked:
                seen.add(nb)
                q.append(path + [nb])

    return []

def _via(graph, src, chk, dst, blocked):
    l1 = _bfs(graph, src, chk, blocked)

    if not l1:
        return []

    l2 = _bfs(graph, chk, dst, blocked)

    if not l2:
        return []

    return l1 + l2[1:]


@riddle('spatial')
class SpatialRiddle(BaseRiddle):
    def generate(self):
        self._deadline = 90

        rng = random.Random(self._seed)
        nodes, graph = _gen_graph(rng)

        src, dst, chk = rng.sample(nodes, 3)
        self._chk = chk

        pool = [n for n in nodes if n not in (src, dst, chk)]
        blocked = set(rng.sample(pool, rng.randint(2, 3)))

        path = _via(graph, src, chk, dst, blocked)

        if not path:
            blocked = set(rng.sample(pool, 1))
            path = _via(graph, src, chk, dst, blocked)

        self._lock(' → '.join(path))
        self._solution_len = len(path)

        ghost, candidates = [], [
            (a, b) for a in nodes for b in nodes
            if a != b and b not in graph.get(a, [])
            and a not in blocked and b not in blocked
        ]

        rng.shuffle(candidates)

        for a, b in candidates[:2]:
            ghost.append(rng.choice(_RUMOURS).format(a=a, b=b))

        vis = {k: [v for v in vs if v not in blocked]
                      for k, vs in graph.items() if k not in blocked}
        edge_lines = [f'  {nd:10s} →  {", ".join(vis[nd])}' for nd in sorted(vis) if vis[nd]]

        text = '\n'.join([
            '┌─ DIRECTED CITY MAZE ──────────────────────────────────────────┐',
            f'│  START      : {src}',
            f'│  DESTINATION: {dst}',
            f'│  CHECKPOINT : must pass through {chk}',
            f'│  IMPASSABLE : {", ".join(sorted(blocked))}',
            '│',
            '│  Confirmed directed edges  (A → B ≠ B → A):',
            *[f'│{l}' for l in edge_lines],
            '│',
            '│  Unverified field reports (may be fabricated):',
            *[f'│  ⚠  {g}' for g in ghost],
            '│',
            f'│  Shortest path: {src} → … → {chk} → … → {dst}',
            '│  Blocked nodes must NOT appear in your answer.',
            '│  Separate waypoints with " → "',
            '└───────────────────────────────────────────────────────────────┘'
        ])

        return {
            'text': text,
            'type': 'spatial',
            'src': src,
            'dst': dst,
            'checkpoint': chk,
            'blocked': sorted(blocked),
            'metadata': {'path_len': len(path)}
        }

    def validate(self, answer):
        result = super().validate(answer)

        if not result['ok']:
            parts = [p.strip() for p in answer.split('→')]

            if hasattr(self, '_chk') and self._chk not in parts:
                result['note'] = 'checkpoint missing'

        return result

    def hint(self, attempt_n):
        return [
            f'The answer has {self._solution_len} waypoints total.',
            'Edges are ONE-WAY.  Verify each hop direction individually.',
            'Discard rumour edges — solve only on confirmed connections.'
        ][min(attempt_n, 2)]
