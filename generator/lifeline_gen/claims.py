"""Exhaustive-search optima for tier-S claims.

These deliberately use exhaustive enumeration (with only safe pruning that never discards
an optimum), not the clever algorithms of Iteration 2.  The validator recomputes every
claim with a different method (dynamic programming / Held-Karp / branch and bound), so
two independent methods must agree.
"""
from itertools import permutations, combinations

from .planted import manhattan


def cargo_opt(crates, cap):
    """Enumerate every subset (depth-first include/exclude); prune only overweight branches
    and branches whose remaining total value cannot beat the best (exact bound)."""
    items = [(c[1], c[2]) for c in crates]
    n = len(items)
    suffix = [0] * (n + 1)
    for i in range(n - 1, -1, -1):
        suffix[i] = suffix[i + 1] + items[i][1]
    best = 0

    def go(i, w, v):
        nonlocal best
        if v > best:
            best = v
        if i == n or v + suffix[i] <= best:
            return
        wi, vi = items[i]
        if w + wi <= cap:
            go(i + 1, w + wi, v + vi)
        go(i + 1, w, v)

    go(0, 0, 0)
    return best


def window_opts(wins):
    """Enumerate every pairwise-compatible set (touching allowed) as an increasing chain."""
    order = sorted(range(len(wins)), key=lambda i: (wins[i][0], wins[i][1]))
    w = [wins[i] for i in order]
    n = len(w)
    best_cnt = best_val = 0

    def go(last_finish, start_idx, cnt, val):
        nonlocal best_cnt, best_val
        best_cnt = max(best_cnt, cnt)
        best_val = max(best_val, val)
        for j in range(start_idx, n):
            if w[j][0] >= last_finish:
                go(w[j][1], j + 1, cnt + 1, val + w[j][2])

    go(-1, 0, 0, 0)
    return best_cnt, best_val


def drum_opt(prices):
    """Enumerate every multiset of piece lengths summing to L."""
    L = len(prices)
    best = 0

    def go(rem, max_piece, val):
        nonlocal best
        if rem == 0:
            best = max(best, val)
            return
        for p in range(min(rem, max_piece), 0, -1):
            go(rem - p, p, val + prices[p - 1])

    go(L, L, 0)
    return best


def tour_opt(pts):
    """Try every order of sites 1..n-1 after site 0."""
    n = len(pts)
    best = None
    for perm in permutations(range(1, n)):
        t = (0,) + perm
        length = sum(manhattan(pts[t[i]], pts[t[(i + 1) % n]]) for i in range(n))
        if best is None or length < best:
            best = length
    return best


def cover_min(n, edges):
    """Smallest k such that some k-subset of nodes touches every edge."""
    for k in range(0, n + 1):
        for sub in combinations(range(n), k):
            s = set(sub)
            if all(u in s or v in s for u, v in edges):
                return k
    return n
