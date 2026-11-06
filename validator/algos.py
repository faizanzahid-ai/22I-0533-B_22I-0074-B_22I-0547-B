"""Independent reference algorithms used by the validator to recompute every field.

None of this is imported from the generator: the validator must not trust the generator.
Where the generator used exhaustive search (tier-S claims), these use a different method
(DP, Held-Karp, branch and bound), so two methods must agree.
"""
import heapq
from collections import deque
from functools import cmp_to_key


# ------------------------------------------------------------------ strings

def kmp_table(p):
    f = [0] * len(p)
    k = 0
    for i in range(1, len(p)):
        while k and p[i] != p[k]:
            k = f[k - 1]
        if p[i] == p[k]:
            k += 1
        f[i] = k
    return f


def kmp_count(text, p):
    """Number of occurrences of p in text, overlaps included (Knuth-Morris-Pratt)."""
    if not p:
        return 0
    f = kmp_table(p)
    k = cnt = 0
    m = len(p)
    for ch in text:
        while k and ch != p[k]:
            k = f[k - 1]
        if ch == p[k]:
            k += 1
        if k == m:
            cnt += 1
            k = f[k - 1]
    return cnt


def edit_distance(a, b):
    """Levenshtein distance (insert, delete, replace), two-row DP."""
    prev = list(range(len(b) + 1))
    for i in range(1, len(a) + 1):
        cur = [i] + [0] * len(b)
        ai = a[i - 1]
        for j in range(1, len(b) + 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ai != b[j - 1]))
        prev = cur
    return prev[-1]


def longest_periodic_run(s, max_period=8):
    """Length of the longest substring that is a repetition of one block of <= max_period symbols."""
    best = 0
    n = len(s)
    for p in range(1, max_period + 1):
        run = 0
        for i in range(n - p):
            if s[i] == s[i + p]:
                run += 1
                if run + p > best:
                    best = run + p
            else:
                run = 0
    return min(best, n)


# ------------------------------------------------------------------ graphs

def build_adj(V, roads, closed=frozenset()):
    adj = [[] for _ in range(V)]
    for (r, u, v, m) in roads:
        if r in closed:
            continue
        adj[u].append((v, m))
        adj[v].append((u, m))
    return adj


def bfs(adj, s):
    d = [-1] * len(adj)
    d[s] = 0
    q = deque([s])
    while q:
        u = q.popleft()
        for v, _ in adj[u]:
            if d[v] < 0:
                d[v] = d[u] + 1
                q.append(v)
    return d


def dijkstra(adj, pen, s):
    INF = float("inf")
    d = [INF] * len(adj)
    d[s] = 0
    pq = [(0, s)]
    while pq:
        du, u = heapq.heappop(pq)
        if du != d[u]:
            continue
        for v, m in adj[u]:
            nd = du + m + pen[v]
            if nd < d[v]:
                d[v] = nd
                heapq.heappush(pq, (nd, v))
    return d


def min_cost_fewest_roads(adj, pen, s):
    """Cheapest cost among the routes with the fewest roads, for every node (DP on BFS layers)."""
    hop = bfs(adj, s)
    INF = float("inf")
    best = [INF] * len(adj)
    best[s] = 0
    layers = {}
    for v, h in enumerate(hop):
        if h >= 0:
            layers.setdefault(h, []).append(v)
    for h in sorted(layers):
        for u in layers[h]:
            for v, m in adj[u]:
                if hop[v] == h + 1:
                    best[v] = min(best[v], best[u] + m + pen[v])
    return best


# ------------------------------------------------------------------ optimisation

def knapsack(items, cap):
    """0/1 knapsack by DP over capacity.  items = [(weight, value)]."""
    best = [0] * (cap + 1)
    for w, v in items:
        for x in range(cap, w - 1, -1):
            if best[x - w] + v > best[x]:
                best[x] = best[x - w] + v
    return best[cap]


def greedy_ratio(items, cap):
    """Decreasing value/kg (exact comparison, ties by crate order), skip what does not fit."""
    idx = list(range(len(items)))

    def cmp(i, j):
        a = items[i][1] * items[j][0]
        b = items[j][1] * items[i][0]
        return -1 if a > b else (1 if a < b else (i > j) - (i < j))

    idx.sort(key=cmp_to_key(cmp))
    left = cap
    val = 0
    for i in idx:
        if items[i][0] <= left:
            left -= items[i][0]
            val += items[i][1]
    return val


def max_compatible_count(wins):
    """Earliest-finish greedy (touching windows are compatible)."""
    cnt, last = 0, -1
    for s, f, _ in sorted(wins, key=lambda w: w[1]):
        if s >= last:
            cnt += 1
            last = f
    return cnt


def max_compatible_value(wins):
    """Weighted interval scheduling DP with binary search."""
    import bisect
    w = sorted(wins, key=lambda x: x[1])
    fins = [x[1] for x in w]
    dp = [0] * (len(w) + 1)
    for i, (s, f, v) in enumerate(w, 1):
        j = bisect.bisect_right(fins, s, 0, i - 1)
        dp[i] = max(dp[i - 1], dp[j] + v)
    return dp[-1]


def rod_cut(prices):
    L = len(prices)
    best = [0] * (L + 1)
    for n in range(1, L + 1):
        best[n] = max(prices[j - 1] + best[n - j] for j in range(1, n + 1))
    return best[L]


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def held_karp(pts):
    """Exact shortest closed tour through all points (Held-Karp DP), tour starts at point 0."""
    n = len(pts)
    if n == 1:
        return 0
    D = [[manhattan(pts[i], pts[j]) for j in range(n)] for i in range(n)]
    INF = float("inf")
    full = 1 << (n - 1)
    dp = [[INF] * n for _ in range(full)]
    for j in range(1, n):
        dp[1 << (j - 1)][j] = D[0][j]
    for mask in range(1, full):
        row = dp[mask]
        for j in range(1, n):
            if row[j] == INF:
                continue
            for k in range(1, n):
                bit = 1 << (k - 1)
                if not mask & bit:
                    nv = row[j] + D[j][k]
                    if nv < dp[mask | bit][k]:
                        dp[mask | bit][k] = nv
    return min(dp[full - 1][j] + D[j][0] for j in range(1, n))


def nearest_neighbour_length(pts):
    """Closed length of the tour from site 0 that always visits the nearest unvisited site
    (ties: smaller site number)."""
    n = len(pts)
    seen = [False] * n
    seen[0] = True
    cur, total = 0, 0
    for _ in range(n - 1):
        best, bd = -1, None
        for j in range(n):
            if not seen[j]:
                d = manhattan(pts[cur], pts[j])
                if bd is None or d < bd:
                    best, bd = j, d
        seen[best] = True
        total += bd
        cur = best
    return total + manhattan(pts[cur], pts[0])


def min_vertex_cover(n, edges):
    """Exact minimum vertex cover by branch and bound on an uncovered edge (pick u or v)."""
    best = [n]

    def go(rem, size):
        if size >= best[0]:
            return
        if not rem:
            best[0] = size
            return
        u, v = rem[0]
        for x in (u, v):
            go([e for e in rem if x not in e], size + 1)

    go(list(edges), 0)
    return best[0]
