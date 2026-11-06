"""Crates (module A data): category mix, weights, values, expiry hours, serials, capacity."""
import math
from functools import cmp_to_key

# Category weights per scenario: 0 Food, 1 Water, 2 Medicine, 3 Tool, 4 Rare.
CAT_WEIGHTS = {
    1: [34, 30, 14, 14, 8],    # flood: food and water dominate
    2: [14, 14, 30, 26, 16],   # earthquake: medicine and tools
    3: [24, 24, 20, 20, 12],
    4: [18, 18, 22, 22, 20],   # urban: rare kit is available
    5: [24, 20, 20, 26, 10],
    6: [10, 32, 34, 14, 10],   # outbreak: medicine and water
}
# Typical (weight range, value range) per category.
CAT_PROFILE = {
    0: ((6, 20), (10, 60)),    # food: heavy, cheap
    1: ((8, 20), (15, 65)),    # water: heaviest
    2: ((1, 8), (40, 100)),    # medicine: light, valuable
    3: ((3, 16), (25, 85)),    # tools
    4: ((1, 12), (60, 100)),   # rare equipment
}


def _fix_share(rng, cats, wanted, pct, pool):
    """Raise the share of categories in `wanted` to at least pct percent."""
    n = len(cats)
    need = math.ceil(pct * n / 100)
    idx = [i for i in range(n) if cats[i] not in wanted]
    rng.shuffle(idx)
    while sum(1 for c in cats if c in wanted) < need:
        cats[idx.pop()] = rng.choice(pool)


def make_crate(rng, cat, scenario):
    (wl, wh), (vl, vh) = CAT_PROFILE[cat]
    w = rng.randint(wl, wh)
    v = rng.randint(vl, vh)
    if scenario == 6:      # supplies spoil early in the camp
        e = rng.randint(0, 300) if rng.random() < 0.65 else rng.randint(301, 999)
    elif cat in (0, 1):   # food and water expire within weeks
        e = rng.randint(48, 720)
    else:
        e = rng.randint(0, 999)
    return [cat, w, v, e]


def gen_crates(rng, n, scenario):
    cats = rng.choices(range(5), weights=CAT_WEIGHTS[scenario], k=n)
    if scenario == 1:
        _fix_share(rng, cats, {0, 1}, 58, [0, 1])
    elif scenario == 2:
        _fix_share(rng, cats, {2, 3}, 48, [2, 3])
    elif scenario == 4:
        _fix_share(rng, cats, {4}, 12, [4])
    elif scenario == 6:
        _fix_share(rng, cats, {1, 2}, 58, [1, 2])
    crates = [make_crate(rng, c, scenario) for c in cats]
    if scenario == 6:      # at least half expire by hour 300
        late = [i for i in range(n) if crates[i][3] > 300]
        rng.shuffle(late)
        while sum(1 for c in crates if c[3] <= 300) * 2 < n:
            crates[late.pop()][3] = rng.randint(0, 300)
    serials = rng.sample(range(10_000_000, 100_000_000), n)
    return [c + [s] for c, s in zip(crates, serials)]   # [cat, weight, value, expiry, serial]


def choose_capacity(rng, crates, lo=0.25, hi=0.55):
    total = sum(c[1] for c in crates)
    cap = round(total * rng.uniform(lo, hi))
    cap = max(cap, math.ceil(total / 10), 1)
    cap = min(cap, (7 * total) // 10)
    return cap


def knapsack_dp(crates, cap):
    best = [0] * (cap + 1)
    for c in crates:
        w, v = c[1], c[2]
        for x in range(cap, w - 1, -1):
            if best[x - w] + v > best[x]:
                best[x] = best[x - w] + v
    return best[cap]


def greedy_by_ratio(crates, cap):
    """Take crates in decreasing value/kg (ties: lower crate_id first), skip what does not fit."""
    order = list(range(len(crates)))

    def cmp(i, j):
        a = crates[i][2] * crates[j][1]
        b = crates[j][2] * crates[i][1]
        if a != b:
            return -1 if a > b else 1
        return -1 if i < j else (1 if i > j else 0)

    order.sort(key=cmp_to_key(cmp))
    left, val = cap, 0
    for i in order:
        if crates[i][1] <= left:
            left -= crates[i][1]
            val += crates[i][2]
    return val
