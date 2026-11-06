"""The four hostile trap cases (46-49)."""
from .config import ALPHABET, PATTERN_LENGTHS
from .inventory import knapsack_dp, greedy_by_ratio
from .network import _road_attrs
from .radio import count_occurrences


def dock_order_crates(rng, n):
    """Case 46: the list arrives already sorted - weight non-decreasing, value non-increasing,
    hence value-per-kg non-increasing, and serial non-decreasing (4 monotone fields)."""
    weights = sorted(rng.randint(1, 20) for _ in range(n))
    values = sorted((rng.randint(10, 100) for _ in range(n)), reverse=True)
    serials = sorted(rng.sample(range(10_000_000, 100_000_000), n))
    cats = rng.choices(range(5), weights=[10, 32, 34, 14, 10], k=n)
    out = []
    for i in range(n):
        out.append([cats[i], weights[i], values[i], rng.randint(0, 999), serials[i]])
    return out


def best_looking_crates(rng, n):
    """Case 47: one tiny 'bait' crate with the best value/kg, one or two 20 kg crates worth
    almost 100, and low-value fillers of 10-13 kg.  Capacity 20.
    Greedy by value/kg takes the bait (1 kg), can no longer fit a 20 kg crate, adds one filler
    and stops: at most 30 + 15 = 45, while the optimum is one big crate (>= 90)."""
    while True:
        crates = [[2, 1, rng.randint(20, 30), rng.randint(0, 300)]]             # bait (medicine)
        for _ in range(rng.randint(1, 2)):
            crates.append([4, 20, rng.randint(90, 100), rng.randint(0, 999)])  # rare kit
        while len(crates) < n:
            crates.append([rng.choice((1, 2)), rng.randint(10, 13), rng.randint(10, 15), rng.randint(0, 600)])
        rng.shuffle(crates)
        serials = rng.sample(range(10_000_000, 100_000_000), n)
        crates = [c + [s] for c, s in zip(crates, serials)]
        cap = 20
        total = sum(c[1] for c in crates)
        if 10 * cap < total or 10 * cap > 7 * total:
            continue
        opt, gr = knapsack_dp(crates, cap), greedy_by_ratio(crates, cap)
        if gr * 10 <= opt * 6:
            return crates, cap


def shortest_looks_cheapest(rng, V):
    """Case 48: a backbone highway of P >= 520 roads (so two locations are >= 520 roads
    apart), side villages attached only to neighbouring backbone positions (no shortcuts),
    and a gadget next to the HQ:  HQ-a-T is 2 roads of ~60 minutes through a penalty-6
    junction; HQ-b1-b2-T is 3 roads of 1-3 minutes.  Every fewest-roads route to T costs
    >= 1.5x the cheapest."""
    P = rng.randint(520, 600)
    # node ids before relabelling: 0 = HQ, 1..P backbone, P+1..P+4 gadget, rest villages
    a, b1, b2, T = P + 1, P + 2, P + 3, P + 4
    pos = {0: 0}
    roads = {}
    deg = [0] * V

    def add(u, v, m, c):
        key = (min(u, v), max(u, v))
        if key in roads:
            return False
        roads[key] = (m, c)
        deg[u] += 1
        deg[v] += 1
        return True

    for i in range(1, P + 1):
        pos[i] = i
        add(i - 1, i, *_road_attrs(rng, 0.03 + rng.random() * 0.05, 1))
    add(0, a, rng.randint(55, 60), rng.randint(20, 60))
    add(a, T, rng.randint(55, 60), rng.randint(20, 60))
    add(0, b1, rng.randint(1, 3), rng.randint(5, 30))
    add(b1, b2, rng.randint(1, 3), rng.randint(5, 30))
    add(b2, T, rng.randint(1, 3), rng.randint(5, 30))
    gadget = {a, b1, b2, T}
    village = list(range(P + 5, V))
    for v in village:
        while True:
            u = rng.randrange(1, v)
            if u not in gadget:
                break
        pos[v] = pos[u]
        add(u, v, *_road_attrs(rng, 0.02 + rng.random() * 0.08, 1))
    extra = rng.randint(V // 5, V // 3)
    tries = 0
    nodes = [v for v in range(1, V) if v not in gadget]
    by_pos = {}
    for v in nodes:
        by_pos.setdefault(pos[v], []).append(v)
    while extra > 0 and tries < 50 * V:
        tries += 1
        u = rng.choice(nodes)
        p = pos[u] + rng.choice((-1, 0, 1))
        if p not in by_pos:
            continue
        v = rng.choice(by_pos[p])
        if v != u and add(u, v, *_road_attrs(rng, 0.02 + rng.random() * 0.06, 1)):
            extra -= 1
    types = ["D"] + rng.choices("SHJD", weights=(30, 10, 52, 8), k=V - 1)
    pen = [0] + rng.choices((0, 1, 2, 4, 6), weights=(18, 17, 27, 22, 16), k=V - 1)
    types[T], pen[T] = "H", rng.randint(0, 2)
    types[a], pen[a] = "J", 6
    types[b1], pen[b1] = "J", 0
    types[b2], pen[b2] = "J", 0
    road_list = [(u, v, m, c) for (u, v), (m, c) in sorted(roads.items())]
    return road_list, types, pen, T


def near_miss_log(rng, N):
    """Case 49: >= 92% of the log is one symbol repeated (block length 1, a stuck carrier).
    Every pattern is (len-1) copies of that symbol plus one other symbol, so its first len-1
    symbols match at ~92% of start positions while the whole pattern almost never matches."""
    block = rng.choice("AEO")
    others = [c for c in ALPHABET if c != block]
    reps = int(N * rng.uniform(0.92, 0.95))
    hit = rng.choice(others)
    tail = [hit] + rng.choices(others, k=N - reps - 1)
    log = block * reps + "".join(tail)
    miss = rng.choice([c for c in others if c != hit])
    pats = []
    for i, L in enumerate(PATTERN_LENGTHS):
        end = hit if i < 4 else (miss if i == 5 else rng.choice(others))
        pats.append(block * (L - 1) + end)
    return log, [(p, count_occurrences(log, p)) for p in pats]
