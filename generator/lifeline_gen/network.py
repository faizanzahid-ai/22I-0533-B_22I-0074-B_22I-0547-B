"""Road network (modules B and F data): locations, roads, closure waves and targets."""
import heapq
import math
from collections import deque

# Probability weights of location types (S, H, J, D) for non-HQ locations.
TYPE_WEIGHTS = {
    1: (30, 10, 52, 8), 2: (20, 20, 52, 8), 3: (42, 10, 40, 8),
    4: (25, 15, 52, 8), 5: (30, 15, 47, 8), 6: (45, 25, 22, 8),
}
# Penalty weights for (0, 1, 2, 4, 6).
PEN_WEIGHTS = {
    1: (18, 17, 27, 22, 16),   # flooded delta: many slow, wet locations
    2: (35, 25, 20, 12, 8), 3: (30, 25, 22, 13, 10), 4: (40, 25, 18, 10, 7),
    5: (30, 25, 22, 13, 10), 6: (40, 25, 20, 10, 5),
}
PENS = (0, 1, 2, 4, 6)


def edge_bounds(V, scenario):
    """Allowed number of roads (inclusive) for a scenario, from V-1..3V and the degree rule."""
    lo, hi = V - 1, min(3 * V, V * (V - 1) // 2)
    if scenario == 1:      # 2.2 <= 2E/V <= 3.2
        lo, hi = max(lo, math.ceil(1.1 * V)), min(hi, (16 * V) // 10)
    elif scenario == 2:    # 2.0 <= 2E/V <= 2.6
        lo, hi = max(lo, V), min(hi, (13 * V) // 10)
    elif scenario == 4:    # 2E/V >= 3.5
        lo = max(lo, math.ceil(1.75 * V))
    elif scenario == 5:    # 2E/V <= 2.4
        hi = min(hi, (12 * V) // 10)
    return lo, hi


def choose_E(rng, V, scenario):
    lo, hi = edge_bounds(V, scenario)
    f = {1: (1.15, 1.5), 2: (1.03, 1.25), 3: (1.3, 1.9), 4: (1.8, 2.5),
         5: (1.0, 1.15), 6: (1.2, 1.8)}[scenario]
    E = round(V * rng.uniform(*f))
    return max(lo, min(hi, E))


def _road_attrs(rng, d, scenario):
    """minutes and cable for a road of geometric length d (unit square)."""
    base = 4 + d * 70
    if rng.random() < 0.3:             # damaged / flooded stretch: much slower
        base *= rng.uniform(1.8, 3.5)
    minutes = max(1, min(60, round(base * rng.uniform(0.6, 1.4))))
    cable = max(1, min(100, round(5 + d * 120 * rng.uniform(0.6, 1.5) + rng.randint(0, 15))))
    return minutes, cable


def build_geographic(rng, V, E, scenario):
    """Spanning tree by nearest-neighbour attachment, then extra short roads."""
    pts = [(rng.random(), rng.random()) for _ in range(V)]
    pts[0] = (0.5, 0.5) if scenario != 5 else pts[0]
    dist = lambda a, b: math.hypot(pts[a][0] - pts[b][0], pts[a][1] - pts[b][1])
    edges = set()
    for i in range(1, V):
        near = heapq.nsmallest(3, range(i), key=lambda j: dist(i, j))
        j = rng.choice(near)
        edges.add((min(i, j), max(i, j)))
    # k nearest neighbours of each node, for extra roads
    knn = [heapq.nsmallest(min(V - 1, 14), (j for j in range(V) if j != i), key=lambda j: dist(i, j))
           for i in range(V)]
    tries = 0
    while len(edges) < E and tries < 50 * E:
        tries += 1
        u = rng.randrange(V)
        v = rng.choice(knn[u][: rng.choice((3, 6, 14))])
        edges.add((min(u, v), max(u, v)))
    while len(edges) < E:                                    # fallback: any pair
        u, v = rng.sample(range(V), 2)
        edges.add((min(u, v), max(u, v)))
    out = []
    for (u, v) in sorted(edges):
        out.append((u, v) + _road_attrs(rng, dist(u, v), scenario))
    return out


def build_corridor(rng, V, E):
    """Landslide corridor: one long highway from the HQ with short side branches.
    Max degree 4.  Returns roads with node 0 = HQ at one end of the highway."""
    P = rng.randint(math.ceil(0.45 * V), math.ceil(0.6 * V))
    P = min(P, V - 1)
    pos = {0: 0}
    deg = [0] * V
    edges = set()

    def add(u, v):
        edges.add((min(u, v), max(u, v)))
        deg[u] += 1
        deg[v] += 1

    for i in range(1, P + 1):          # highway 0-1-2-...-P
        add(i - 1, i)
        pos[i] = i
    for v in range(P + 1, V):          # villages hang off the highway or other villages
        while True:
            u = rng.randrange(v)
            if deg[u] < 3 and u != 0:
                break
        add(u, v)
        pos[v] = pos[u]
    tries = 0
    while len(edges) < E and tries < 5000:    # a few short loops near the highway
        tries += 1
        u, v = rng.sample(range(1, V), 2)
        if abs(pos[u] - pos[v]) <= 2 and deg[u] < 4 and deg[v] < 4 and (min(u, v), max(u, v)) not in edges:
            add(u, v)
    out = []
    for (u, v) in sorted(edges):
        d = 0.02 + rng.random() * 0.12
        out.append((u, v) + _road_attrs(rng, d, 5))
    return out


def relabel(rng, V, roads):
    """Shuffle location ids 1..V-1 (HQ stays 0) so ids carry no structure."""
    perm = list(range(1, V))
    rng.shuffle(perm)
    mp = [0] + perm
    out = []
    for (u, v, m, c) in roads:
        a, b = mp[u], mp[v]
        out.append((min(a, b), max(a, b), m, c))
    out.sort()
    return out


def assign_types(rng, V, scenario):
    types = ["D"] + rng.choices("SHJD", weights=TYPE_WEIGHTS[scenario], k=V - 1)
    others = list(range(1, V))

    def convert(to, need_fn):
        cand = [i for i in others if types[i] in "JD"]
        rng.shuffle(cand)
        while not need_fn() and cand:
            types[cand.pop()] = to

    convert("S", lambda: types.count("S") >= 1)
    convert("H", lambda: types.count("H") >= 1)
    convert("S", lambda: types.count("S") + types.count("H") >= 3)
    if scenario == 3:
        convert("S", lambda: types.count("S") * 4 >= V + 2)
    return types


def assign_penalties(rng, V, scenario):
    pen = [0] + rng.choices(PENS, weights=PEN_WEIGHTS[scenario], k=V - 1)
    if scenario == 1:
        low = [i for i in range(1, V) if pen[i] < 2]
        rng.shuffle(low)
        while sum(1 for p in pen if p >= 2) * 10 < 4 * V + 5:
            if not low:
                break
            pen[low.pop()] = rng.choice((2, 4, 6))
    return pen


def adjacency(V, roads, closed=frozenset()):
    adj = [[] for _ in range(V)]
    for r, (u, v, m, c) in enumerate(roads):
        if r in closed:
            continue
        adj[u].append((v, m))
        adj[v].append((u, m))
    return adj


def bfs(adj, src):
    dist = [-1] * len(adj)
    dist[src] = 0
    q = deque([src])
    while q:
        u = q.popleft()
        for v, _ in adj[u]:
            if dist[v] < 0:
                dist[v] = dist[u] + 1
                q.append(v)
    return dist


def dijkstra(adj, pen, src):
    INF = float("inf")
    d = [INF] * len(adj)
    d[src] = 0
    pq = [(0, src)]
    while pq:
        du, u = heapq.heappop(pq)
        if du > d[u]:
            continue
        for v, m in adj[u]:
            nd = du + m + pen[v]
            if nd < d[v]:
                d[v] = nd
                heapq.heappush(pq, (nd, v))
    return d


def fewest_roads_min_cost(adj, pen, src):
    """For every node: the cheapest cost among routes that use the fewest roads."""
    hop = bfs(adj, src)
    order = sorted((h, v) for v, h in enumerate(hop) if h >= 0)
    INF = float("inf")
    best = [INF] * len(adj)
    best[src] = 0
    for h, u in order:
        for v, m in adj[u]:
            if hop[v] == h + 1 and best[u] + m + pen[v] < best[v]:
                best[v] = best[u] + m + pen[v]
    return best


def bridges(V, adj_list):
    """Bridges of an undirected simple graph (iterative Tarjan). adj_list[u] = [(v, road_no)]."""
    disc = [-1] * V
    low = [0] * V
    out = []
    t = 0
    for s in range(V):
        if disc[s] >= 0:
            continue
        stack = [(s, -1, iter(adj_list[s]))]
        disc[s] = low[s] = t
        t += 1
        while stack:
            u, pe, it = stack[-1]
            nxt = next(it, None)
            if nxt is None:
                stack.pop()
                if stack:
                    p = stack[-1][0]
                    low[p] = min(low[p], low[u])
                    if low[u] > disc[p]:
                        out.append(pe)
                continue
            v, r = nxt
            if r == pe:
                continue
            if disc[v] < 0:
                disc[v] = low[v] = t
                t += 1
                stack.append((v, r, iter(adj_list[v])))
            else:
                low[u] = min(low[u], disc[v])
    return out


def make_waves(rng, E, n_waves, forced=None):
    """n_waves disjoint lists of road numbers, each of size 1..max(1, E//4)."""
    cap = max(1, E // 4)
    pool = list(range(E))
    rng.shuffle(pool)
    if forced is not None:
        pool.remove(forced)
    waves = []
    for w in range(n_waves):
        size = rng.randint(1, min(cap, 2 + E // 25))
        wave = [pool.pop() for _ in range(size)]
        if w == 0 and forced is not None:
            if len(wave) >= cap:
                wave.pop()
            wave.append(forced)
        waves.append(sorted(wave))
    return waves
