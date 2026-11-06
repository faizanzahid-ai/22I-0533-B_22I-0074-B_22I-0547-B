"""Rescue windows (module C) and incident alarms (module D)."""
import bisect


def overlap_total(wins):
    """Sum over windows of the number of other windows it strictly overlaps
    (touching does not count).  O(n log n) with two sorted lists."""
    starts = sorted(w[0] for w in wins)
    fins = sorted(w[1] for w in wins)
    n = len(wins)
    tot = 0
    for s, f, _ in wins:
        not_after = n - bisect.bisect_left(starts, f)      # others starting at/after f
        not_before = bisect.bisect_right(fins, s)          # others finishing at/before s
        tot += n - 1 - not_after - not_before
    return tot


def touching_pairs(wins):
    starts = {}
    for s, f, _ in wins:
        starts[s] = starts.get(s, 0) + 1
    return sum(starts.get(f, 0) for s, f, _ in wins)


def gen_windows(rng, n, scenario, tier):
    wins = []
    if scenario == 3:
        # storm-surge pulses: short rescue windows packed around a few surge times
        centres = [rng.randint(120, 1320) for _ in range(rng.randint(2, 4) if tier != "S" else 1)]
        for _ in range(n):
            c = rng.choice(centres)
            d = rng.randint(20, 120)
            s = max(0, min(1440 - d, c + rng.randint(-60, 60) - d // 2))
            wins.append([s, s + d, rng.randint(1, 100)])
    else:
        for _ in range(n):
            if rng.random() < 0.6:
                d = rng.randint(5, 120)
            else:
                d = rng.randint(121, 480)
            s = rng.randint(0, 1440 - d)
            # value grows with duration but is noisy
            v = max(1, min(100, round(d / 6 + rng.randint(-15, 50))))
            wins.append([s, s + d, v])
    # plant touching pairs: window j starts exactly when window i finishes
    want = max(2, n // 15)
    used = set()
    idx = list(range(n))
    rng.shuffle(idx)
    planted = 0
    while planted < want and len(idx) >= 2:
        i = idx.pop()
        j = idx.pop()
        f = wins[i][1]
        d = rng.randint(5, 90)
        if f + d <= 1440:
            wins[j][0], wins[j][1] = f, f + d
            planted += 1
            used.update((i, j))
    return [tuple(w) for w in wins]


def gen_incidents(rng, n, scenario, tier):
    lo, hi = (1.55, 1.75) if scenario == 4 else (1.25, 1.75)
    T = round(n / rng.uniform(lo, hi))
    lo_q, hi_q = (15, 18) if scenario == 4 else (12, 18)
    while 10 * n > hi_q * T:
        T += 1
    while 10 * n < lo_q * T:
        T -= 1
    if scenario == 2:          # bursts of urgent calls after each aftershock
        shocks = sorted(rng.randrange(T) for _ in range(rng.randint(3, 6)))
        ticks = []
        for _ in range(n - 2):
            if rng.random() < 0.65:
                t = rng.choice(shocks) + int(rng.expovariate(1 / max(1, T / 20)))
                ticks.append(min(T - 1, t))
            else:
                ticks.append(rng.randrange(T))
    else:
        ticks = [rng.randrange(T) for _ in range(n - 2)]
    ticks = sorted(ticks + [0, T - 1])
    if scenario == 2:
        weights = [2, 2, 3, 4, 6, 9, 13, 16, 17, 14]
    elif scenario == 4:
        weights = [8, 8, 9, 10, 11, 12, 12, 11, 10, 9]
    else:
        weights = [12, 12, 11, 11, 10, 10, 10, 9, 8, 7]
    pr = rng.choices(range(1, 11), weights=weights, k=n)
    # at least 6 distinct priorities including 1
    need = [1] + rng.sample(range(2, 11), 5)
    pos = rng.sample(range(n), len(need))
    for p, i in zip(need, pos):
        if p not in pr:
            pr[i] = p
    if 1 not in pr:
        pr[pos[0]] = 1
    if scenario == 2:          # mean priority >= 6.0
        idx = [i for i in range(n) if 1 < pr[i] < 10]
        rng.shuffle(idx)
        s = sum(pr)
        while s * 10 < 61 * n and idx:
            i = idx.pop()
            s += 10 - pr[i]
            pr[i] = 10
    return list(zip(ticks, pr))
