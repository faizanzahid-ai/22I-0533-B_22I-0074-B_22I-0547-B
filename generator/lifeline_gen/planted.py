"""Planted objects (modules G, H, I): sites + tour, pipeline, drum prices, sensor graph + cover,
safety rules + satisfying assignment, rations + planted selection.

Every planted object is correct by construction: the cover is chosen first and every edge
is given an endpoint in it; the assignment is chosen first and every rule is made true
under it; the ration selection is chosen first and the target is its sum.
"""


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def tour_length(pts, tour):
    return sum(manhattan(pts[tour[i]], pts[tour[(i + 1) % len(tour)]]) for i in range(len(tour)))


def gen_sites(rng, n, scenario):
    seen = set()
    pts = []
    clusters = [(rng.randint(100, 900), rng.randint(100, 900)) for _ in range(rng.randint(2, 5))]
    while len(pts) < n:
        if scenario in (5,):            # sites strung along a valley
            t = rng.randint(0, 999)
            p = (t, max(0, min(999, 500 + (t - 500) // 3 + rng.randint(-60, 60))))
        elif rng.random() < 0.6:        # villages / camp blocks
            cx, cy = rng.choice(clusters)
            p = (max(0, min(999, cx + rng.randint(-120, 120))), max(0, min(999, cy + rng.randint(-120, 120))))
        else:
            p = (rng.randint(0, 999), rng.randint(0, 999))
        if p not in seen:
            seen.add(p)
            pts.append(p)
    return pts


def nearest_neighbour_tour(pts):
    """Always go to the nearest unvisited site (ties: smaller site number)."""
    n = len(pts)
    seen = [False] * n
    tour = [0]
    seen[0] = True
    cur = 0
    for _ in range(n - 1):
        best, bd = -1, None
        for j in range(n):
            if not seen[j]:
                d = manhattan(pts[cur], pts[j])
                if bd is None or d < bd:
                    best, bd = j, d
        tour.append(best)
        seen[best] = True
        cur = best
    return tour


def two_opt(pts, tour, max_passes=4):
    """Strictly improving 2-opt moves; site 0 stays first."""
    n = len(tour)
    t = list(tour)
    for _ in range(max_passes):
        improved = False
        for i in range(1, n - 1):
            a, b = pts[t[i - 1]], pts[t[i]]
            for j in range(i + 1, n):
                c, d = pts[t[j]], pts[t[(j + 1) % n]]
                delta = manhattan(a, c) + manhattan(b, d) - manhattan(a, b) - manhattan(c, d)
                if delta < 0:
                    t[i:j + 1] = reversed(t[i:j + 1])
                    b = pts[t[i]]
                    improved = True
        if not improved:
            break
    return t


def gen_pipeline(rng, n):
    return [rng.randint(2, 100) for _ in range(n + 1)]


def gen_drum(rng, L):
    """price(j) ~ A * j^g with noise and a premium on standard lengths; 1..500, not proportional."""
    g = rng.uniform(0.75, 1.05) if L <= 14 else rng.uniform(0.7, 0.95)
    top = rng.randint(250, 480)
    A = top / (L ** g)
    std = rng.randint(2, max(2, L // 3))
    prices = []
    for j in range(1, L + 1):
        p = A * (j ** g) * rng.uniform(0.85, 1.15)
        if j % std == 0:
            p *= 1.12
        prices.append(max(1, min(500, round(p))))
    if all(prices[j - 1] * 1 == prices[0] * j for j in range(1, L + 1)):
        prices[-1] = max(1, prices[-1] - 1)
    return prices


def gen_sensors(rng, n):
    k = rng.randint(2, max(2, n // 3 + 1))
    k = min(k, n // 2)
    cover = sorted(rng.sample(range(n), k))
    cset = set(cover)
    edges = set()
    for v in range(n):                         # every outside node is watched by some cover node
        if v not in cset:
            u = rng.choice(cover)
            edges.add((min(u, v), max(u, v)))
    max_e = k * (n - k) + k * (k - 1) // 2
    m = min(max_e, rng.randint(n - 1 + k, 2 * n + k))
    while len(edges) < m:
        u = rng.choice(cover)
        v = rng.randrange(n)
        if u != v:
            edges.add((min(u, v), max(u, v)))
    return k, cover, sorted(edges)


def gen_safety(rng, v, ratio):
    m = round(ratio * v)
    m = max(2 * v, min(6 * v, m))
    assign = [rng.randint(0, 1) for _ in range(v)]           # assign[j-1] for switch j
    rules = []
    for _ in range(m):
        vs = rng.sample(range(1, v + 1), 3)
        lits = [j if rng.random() < 0.5 else -j for j in vs]
        if not any((l > 0) == (assign[abs(l) - 1] == 1) for l in lits):
            i = rng.randrange(3)
            lits[i] = -lits[i]                               # make one condition true
        rules.append(lits)
    return assign, rules


def gen_rations(rng, n):
    base = rng.randint(40, 400)
    vals = [max(1, min(1000, base + rng.randint(-base // 2, 600))) for _ in range(n)]
    size = rng.randint(max(2, n // 4), max(2, n // 2))
    chosen = set(rng.sample(range(n), size))
    target = sum(vals[i] for i in chosen)
    return vals, [1 if i in chosen else 0 for i in range(n)], target
