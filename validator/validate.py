"""LIFELINE validator.

    python validator/validate.py cases.xlsx                 # full workbook (50 cases)
    python validator/validate.py tests/broken_x.xlsx --subset   # a workbook holding only some cases

Re-reads the workbook, recomputes every derived field with its own algorithms (algos.py) and
prints PASS or the broken rules for every case.  Exit code 0 only if everything passes.
Check tags follow Section 4 of the statement (V1..V8).
"""
import argparse
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import algos  # noqa: E402

try:
    from openpyxl import load_workbook
except ImportError:  # pragma: no cover
    sys.exit("openpyxl is required: pip install openpyxl")

ALPHABET = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-")
PATTERN_LENGTHS = [2, 4, 8, 12, 20, 40]

SHEETS = [
    ("cases", ["case_id", "group_seed", "case_no", "tier", "scenario", "capacity", "target_0",
               "target_1", "target_2", "edit_bound", "tour_length", "sensor_nodes", "sensor_k",
               "safety_vars", "rations_target"]),
    ("crates", ["case_id", "crate_id", "cat", "weight", "value", "expiry", "serial"]),
    ("locations", ["case_id", "loc_id", "type", "penalty"]),
    ("roads", ["case_id", "road_no", "u", "v", "minutes", "cable"]),
    ("waves", ["case_id", "wave_no", "road_no"]),
    ("radio_log", ["case_id", "part", "text"]),
    ("radio_patterns", ["case_id", "pattern_no", "pattern", "count"]),
    ("radio_reports", ["case_id", "report_a", "report_b"]),
    ("windows", ["case_id", "window_id", "start", "finish", "value"]),
    ("incidents", ["case_id", "alarm_id", "tick", "priority"]),
    ("sites", ["case_id", "site_no", "x", "y"]),
    ("tour", ["case_id", "step", "site_no"]),
    ("pipeline_dims", ["case_id", "idx", "dim"]),
    ("drum_prices", ["case_id", "length", "price"]),
    ("sensor_edges", ["case_id", "u", "v"]),
    ("sensor_cover", ["case_id", "node"]),
    ("safety_rules", ["case_id", "rule_no", "lit_1", "lit_2", "lit_3"]),
    ("safety_planted", ["case_id", "switch", "value"]),
    ("rations", ["case_id", "item", "value", "planted"]),
    ("claims", ["case_id", "cargo_opt", "window_count_opt", "window_value_opt", "drum_opt",
                "tour_opt", "cover_min"]),
]
TEXT_COLS = {"case_id", "tier", "type", "text", "pattern", "report_a", "report_b"}

RANGES = {
    "S": dict(crates=(8, 20), V=(6, 12), waves=(2, 5), log=(200, 500), report=(10, 30),
              windows=(8, 20), alarms=(10, 40), sites=(5, 9), stages=(4, 8), drum=(5, 14),
              sensors=(6, 14), safety=(6, 15), rations=(8, 20)),
    "M": dict(crates=(40, 200), V=(30, 150), waves=(2, 5), log=(2000, 10000), report=(30, 150),
              windows=(50, 300), alarms=(200, 1000), sites=(10, 16), stages=(15, 60), drum=(40, 200),
              sensors=(20, 40), safety=(20, 50), rations=(24, 40)),
    "L": dict(crates=(500, 1500), V=(500, 2000), waves=(2, 5), log=(20000, 100000), report=(200, 1000),
              windows=(1000, 3000), alarms=(2000, 5000), sites=(200, 500), stages=(100, 300),
              drum=(500, 2000), sensors=(100, 400), safety=(20, 50), rations=(50, 100)),
}
RANGES["X"] = RANGES["L"]
TRAP_RANGES = {46: {"crates": (1500, 3000)}, 47: {"crates": (12, 60)},
               48: {"V": (1500, 3000)}, 49: {"log": (50000, 100000)}}


def tier_of(k):
    return "S" if k < 20 else "M" if k < 40 else "L" if k < 46 else "X"


def rng_of(k, item):
    if k in TRAP_RANGES and item in TRAP_RANGES[k]:
        return TRAP_RANGES[k][item]
    return RANGES[tier_of(k)][item]


class Errors:
    def __init__(self):
        self.items = []

    def add(self, tag, msg):
        self.items.append((tag, msg))

    def check(self, cond, tag, msg):
        if not cond:
            self.add(tag, msg)
        return cond

    def __bool__(self):
        return bool(self.items)


def consecutive(vals, start):
    return list(vals) == list(range(start, start + len(vals)))


# ====================================================================== reading + V1

def read_workbook(path, errs):
    wb = load_workbook(path, read_only=True, data_only=False)
    names = wb.sheetnames
    want = [n for n, _ in SHEETS]
    errs.check(names == want, "V1", f"sheets must be exactly {want} in this order, found {names}")
    data = {}
    for name, header in SHEETS:
        if name not in names:
            data[name] = []
            continue
        ws = wb[name]
        it = ws.iter_rows(values_only=True)
        head = next(it, None)
        head = [h for h in (head or [])]
        while head and head[-1] is None:
            head.pop()
        errs.check(head == header, "V1", f"sheet {name}: header must be {header}, found {head}")
        rows = []
        for r_i, row in enumerate(it, 2):
            row = list(row)
            while len(row) > len(header) and row[-1] is None:
                row.pop()
            if all(v is None for v in row):
                errs.add("V1", f"sheet {name}: empty row {r_i}")
                continue
            if len(row) != len(header):
                errs.add("V1", f"sheet {name}: row {r_i} has {len(row)} cells, expected {len(header)}")
                continue
            bad = False
            for col, val in zip(header, row):
                if col in TEXT_COLS:
                    if not isinstance(val, str) or not val.isascii():
                        errs.add("V1", f"sheet {name}: row {r_i} column {col} must be ASCII text, got {val!r}")
                        bad = True
                    elif isinstance(val, str) and val.startswith("="):
                        errs.add("V1", f"sheet {name}: row {r_i} holds a formula")
                        bad = True
                elif not (isinstance(val, int) and not isinstance(val, bool)):
                    errs.add("V1", f"sheet {name}: row {r_i} column {col} must be an integer, got {val!r}")
                    bad = True
            if not bad:
                rows.append(tuple(row))
        # sorted by case_id, then by the second column
        keys = [(r[0], r[1]) for r in rows]
        if keys != sorted(keys):
            errs.add("V1", f"sheet {name}: rows are not sorted by case_id then {header[1]}")
        data[name] = rows
    wb.close()
    return data


# ====================================================================== one case

def check_case(cid, crow, D, errs, facts):
    """D[sheet] = rows of this case (case_id stripped).  facts collects data for variety rules."""
    (seed, k, tier, scen, cap, t0, t1, t2, edit_bound, tour_len,
     s_nodes, s_k, s_vars, r_target) = crow
    R = lambda item: rng_of(k, item)  # noqa: E731
    E_ = errs

    def inr(x, item, what):
        lo, hi = R(item)
        return E_.check(lo <= x <= hi, "V2", f"{what} = {x} outside {lo}..{hi}")

    # ---------------------------------------------------------------- crates
    cr = D["crates"]
    n = len(cr)
    inr(n, "crates", "number of crates")
    E_.check(consecutive([r[0] for r in cr], 1), "V3", "crate_id must run 1, 2, 3, ...")
    for (cid_, cat, w, v, e, s) in cr:
        E_.check(0 <= cat <= 4, "V2", f"crate {cid_}: cat {cat} not in 0..4")
        E_.check(1 <= w <= 20, "V2", f"crate {cid_}: weight {w} not in 1..20")
        E_.check(10 <= v <= 100, "V2", f"crate {cid_}: value {v} not in 10..100")
        E_.check(0 <= e <= 999, "V2", f"crate {cid_}: expiry {e} not in 0..999")
        E_.check(10_000_000 <= s <= 99_999_999, "V2", f"crate {cid_}: serial {s} not 8 digits")
    E_.check(len({r[5] for r in cr}) == n, "V3", "serials are not distinct")
    W = sum(r[2] for r in cr)
    E_.check(cap >= 1 and 10 * cap >= W and 10 * cap <= 7 * W, "V2",
             f"capacity {cap} not within 10%..70% of total weight {W}")
    items = [(r[2], r[3]) for r in cr if r[2] >= 1]

    # ---------------------------------------------------------------- locations / roads
    loc = D["locations"]
    V = len(loc)
    inr(V, "V", "number of locations V")
    E_.check(consecutive([r[0] for r in loc], 0), "V3", "loc_id must run 0..V-1")
    types = [r[1] for r in loc]
    pen = [r[2] for r in loc]
    for (i, t, p) in loc:
        E_.check(t in ("D", "S", "H", "J"), "V2", f"location {i}: type {t!r} not in D/S/H/J")
        E_.check(p in (0, 1, 2, 4, 6), "V2", f"location {i}: penalty {p} not in {{0,1,2,4,6}}")
    if loc:
        E_.check(loc[0][1] == "D" and loc[0][2] == 0, "V2", "location 0 (HQ) must be type D with penalty 0")
    E_.check("S" in types and "H" in types, "V2", "need at least one shelter (S) and one hospital (H)")

    rd = D["roads"]
    E = len(rd)
    E_.check(V - 1 <= E <= 3 * V, "V2", f"number of roads E = {E} outside V-1..3V ({V - 1}..{3 * V})")
    E_.check(consecutive([r[0] for r in rd], 0), "V3", "road_no must run 0, 1, ...")
    pairs = set()
    road_ok = True
    for (r, u, v, m, c) in rd:
        if not (0 <= u < v < V):
            E_.add("V3", f"road {r}: ends ({u},{v}) must satisfy 0 <= u < v < V")
            road_ok = False
        if (u, v) in pairs:
            E_.add("V3", f"road {r}: repeated pair ({u},{v})")
        pairs.add((u, v))
        E_.check(1 <= m <= 60, "V2", f"road {r}: minutes {m} not in 1..60")
        E_.check(1 <= c <= 100, "V2", f"road {r}: cable {c} not in 1..100")
    g = [(r, u, v, m) for (r, u, v, m, c) in rd]
    adj = algos.build_adj(V, g) if road_ok and V else None
    hop = None
    if adj is not None:
        hop = algos.bfs(adj, 0)
        E_.check(min(hop) >= 0, "V4", f"network is not connected before closures "
                                      f"({sum(1 for h in hop if h < 0)} locations unreachable)")

    targets = [t0, t1, t2]
    E_.check(len(set(targets)) == 3, "V3", f"targets {targets} are not distinct")
    for t in targets:
        if E_.check(0 <= t < V, "V3", f"target {t} is not a location"):
            E_.check(t != 0 and types[t] in ("S", "H"), "V3", f"target {t} must be a shelter or hospital, not the HQ")

    # ---------------------------------------------------------------- waves
    wv = D["waves"]
    by_wave = defaultdict(list)
    for (w, r) in wv:
        by_wave[w].append(r)
    nw = len(by_wave)
    inr(nw, "waves", "number of closure waves")
    E_.check(sorted(by_wave) == list(range(1, nw + 1)), "V3", "wave_no must run 1, 2, ...")
    seen = Counter(r for (_, r) in wv)
    for (w, r) in wv:
        E_.check(0 <= r < E, "V3", f"wave {w}: road {r} does not exist")
    dup = [r for r, c in seen.items() if c > 1]
    E_.check(not dup, "V4", f"waves are not disjoint: roads {dup[:5]} closed more than once")
    lim = max(1, E // 4)
    for w, rs in by_wave.items():
        E_.check(1 <= len(rs) <= lim, "V4", f"wave {w} has {len(rs)} roads, allowed 1..{lim}")

    # ---------------------------------------------------------------- radio
    lg = D["radio_log"]
    E_.check(consecutive([r[0] for r in lg], 1), "V5", "radio_log parts must run 1, 2, ... in order")
    for (p, text) in lg:
        E_.check(1 <= len(text) <= 10_000, "V5", f"radio_log part {p} has {len(text)} symbols (max 10,000)")
    log = "".join(r[1] for r in lg)
    bad = set(log) - ALPHABET
    E_.check(not bad, "V2", f"radio log uses symbols outside the alphabet: {sorted(bad)[:5]}")
    inr(len(log), "log", "radio log length")

    pt = D["radio_patterns"]
    E_.check([r[0] for r in pt] == list(range(6)), "V3", "exactly six patterns, pattern_no 0..5")
    E_.check([len(r[1]) for r in pt] == PATTERN_LENGTHS, "V2",
             f"pattern lengths must be {PATTERN_LENGTHS}, found {[len(r[1]) for r in pt]}")
    true_counts = []
    for (i, p, cnt) in pt:
        E_.check(not (set(p) - ALPHABET), "V2", f"pattern {i} uses symbols outside the alphabet")
        tc = algos.kmp_count(log, p)
        true_counts.append(tc)
        E_.check(cnt == tc, "V5", f"pattern {i}: count {cnt} but it occurs {tc} times")
    E_.check(sum(1 for c in true_counts if c > 0) >= 2, "V5", "at least two patterns must occur")
    E_.check(any(c == 0 for c in true_counts), "V5", "at least one pattern must not occur")

    rp = D["radio_reports"]
    if E_.check(len(rp) == 1, "V3", f"need exactly one radio_reports row, found {len(rp)}"):
        a, b = rp[0]
        inr(len(a), "report", "length of report_a")
        inr(len(b), "report", "length of report_b")
        E_.check(not ((set(a) | set(b)) - ALPHABET), "V2", "reports use symbols outside the alphabet")
        d = algos.edit_distance(a, b)
        E_.check(d <= edit_bound <= len(a) + len(b), "V5",
                 f"edit_bound {edit_bound} must be within true distance {d} .. {len(a) + len(b)}")

    # ---------------------------------------------------------------- windows
    wn = D["windows"]
    inr(len(wn), "windows", "number of windows")
    E_.check(consecutive([r[0] for r in wn], 1), "V3", "window_id must run 1, 2, ...")
    wins = []
    for (i, s, f, v) in wn:
        ok = E_.check(0 <= s < f <= 1440, "V2", f"window {i}: needs 0 <= start < finish <= 1440 ({s},{f})")
        ok &= E_.check(5 <= f - s <= 480, "V2", f"window {i}: duration {f - s} not in 5..480")
        ok &= E_.check(1 <= v <= 100, "V2", f"window {i}: value {v} not in 1..100")
        wins.append((s, f, v))
    if len(wins) >= 8:
        starts = Counter(s for s, _, _ in wins)
        touch = sum(starts.get(f, 0) for _, f, _ in wins)
        E_.check(touch >= 2, "V2", f"only {touch} touching window pairs, need at least 2")

    # ---------------------------------------------------------------- incidents
    inc = D["incidents"]
    na = len(inc)
    inr(na, "alarms", "number of alarms")
    E_.check(consecutive([r[0] for r in inc], 1), "V3", "alarm_id must run 1, 2, ...")
    ticks = [r[1] for r in inc]
    prs = [r[2] for r in inc]
    if ticks:
        E_.check(ticks[0] == 0, "V2", "first tick must be 0")
        E_.check(all(ticks[i] <= ticks[i + 1] for i in range(len(ticks) - 1)), "V2", "ticks decrease")
    E_.check(all(1 <= p <= 10 for p in prs), "V2", "priority outside 1..10")
    if tier in ("M", "L", "X") and ticks:
        T = ticks[-1] + 1
        E_.check(12 * T <= 10 * na <= 18 * T, "V2",
                 f"alarms per tick {na}/{T} = {na / T:.3f} outside 1.2..1.8")
        E_.check(len(set(prs)) >= 6 and 1 in prs, "V2", "need >= 6 distinct priorities including 1")

    # ---------------------------------------------------------------- sites / tour
    st = D["sites"]
    ns = len(st)
    inr(ns, "sites", "number of relief sites")
    E_.check(consecutive([r[0] for r in st], 0), "V3", "site_no must run 0..n-1")
    pts = [(x, y) for (_, x, y) in st]
    E_.check(all(0 <= x <= 999 and 0 <= y <= 999 for x, y in pts), "V2", "site coordinate outside 0..999")
    E_.check(len(set(pts)) == ns, "V2", "two sites are equal")
    tr = D["tour"]
    E_.check(consecutive([r[0] for r in tr], 0), "V3", "tour step must run 0..n-1")
    tour = [r[1] for r in tr]
    if E_.check(sorted(tour) == list(range(ns)) and tour and tour[0] == 0, "V6",
                "planted tour must be a permutation of all sites starting at site 0"):
        L = sum(algos.manhattan(pts[tour[i]], pts[tour[(i + 1) % ns]]) for i in range(ns))
        E_.check(L == tour_len, "V6", f"tour_length {tour_len} but the planted tour is {L} long")
        if tier in ("L", "X"):
            nn = algos.nearest_neighbour_length(pts)
            E_.check(tour_len <= nn, "V6", f"tour_length {tour_len} longer than nearest-neighbour tour {nn}")

    # ---------------------------------------------------------------- pipeline / drum
    pd = D["pipeline_dims"]
    E_.check(consecutive([r[0] for r in pd], 0), "V3", "pipeline idx must run 0..n")
    inr(len(pd) - 1, "stages", "number of pipeline stages")
    E_.check(all(2 <= r[1] <= 100 for r in pd), "V2", "pipeline dim outside 2..100")
    dr = D["drum_prices"]
    inr(len(dr), "drum", "drum length L")
    E_.check(consecutive([r[0] for r in dr], 1), "V3", "drum length must run 1..L")
    prices = [r[1] for r in dr]
    E_.check(all(1 <= p <= 500 for p in prices), "V2", "drum price outside 1..500")
    if prices:
        E_.check(any(prices[j - 1] != prices[0] * j for j in range(1, len(prices) + 1)), "V2",
                 "drum prices are all proportional to length")

    # ---------------------------------------------------------------- sensors
    inr(s_nodes, "sensors", "sensor_nodes")
    se = D["sensor_edges"]
    sedges = []
    ok_edges = True
    for (u, v) in se:
        if not (0 <= u < v < s_nodes):
            E_.add("V3", f"sensor edge ({u},{v}) invalid (need 0 <= u < v < sensor_nodes)")
            ok_edges = False
        sedges.append((u, v))
    E_.check(len(set(sedges)) == len(sedges), "V3", "repeated sensor edge")
    E_.check(len(sedges) >= s_nodes - 1, "V2", f"{len(sedges)} sensor edges, need at least n - 1")
    cover = [r[0] for r in D["sensor_cover"]]
    E_.check(len(cover) == s_k and len(set(cover)) == s_k, "V6",
             f"sensor_cover must hold sensor_k = {s_k} distinct nodes, found {len(cover)}")
    E_.check(all(0 <= c < s_nodes for c in cover), "V3", "cover node does not exist")
    E_.check(2 <= s_k and 2 * s_k <= s_nodes, "V2", f"sensor_k = {s_k} must satisfy 2 <= k <= n/2")
    cs = set(cover)
    unc = [e for e in sedges if e[0] not in cs and e[1] not in cs]
    E_.check(not unc, "V6", f"planted cover misses {len(unc)} edges, e.g. {unc[:3]}")

    # ---------------------------------------------------------------- safety
    inr(s_vars, "safety", "safety_vars")
    sr = D["safety_rules"]
    m = len(sr)
    E_.check(consecutive([r[0] for r in sr], 1), "V3", "rule_no must run 1, 2, ...")
    E_.check(2 * s_vars <= m <= 6 * s_vars, "V2", f"rules / switches = {m}/{s_vars} outside 2.0..6.0")
    rules = []
    for (i, a1, a2, a3) in sr:
        lits = (a1, a2, a3)
        ok = all(l != 0 and abs(l) <= s_vars for l in lits)
        ok = E_.check(ok, "V3", f"rule {i}: literal refers to a missing switch {lits}") and \
            E_.check(len({abs(l) for l in lits}) == 3, "V2", f"rule {i}: switches not different {lits}")
        if ok:
            rules.append(lits)
    sp = D["safety_planted"]
    E_.check(consecutive([r[0] for r in sp], 1) and len(sp) == s_vars, "V3",
             "safety_planted must list switches 1..safety_vars")
    val = {r[0]: r[1] for r in sp}
    E_.check(all(v in (0, 1) for v in val.values()), "V2", "planted switch value not 0/1")
    broken = [i for i, lits in enumerate(rules, 1)
              if not any((l > 0) == (val.get(abs(l)) == 1) for l in lits)]
    E_.check(not broken, "V6", f"planted assignment breaks {len(broken)} rules, e.g. rule {broken[:3]}")

    # ---------------------------------------------------------------- rations
    ra = D["rations"]
    inr(len(ra), "rations", "number of ration quantities")
    E_.check(consecutive([r[0] for r in ra], 0), "V3", "ration item must run 0, 1, ...")
    E_.check(all(1 <= r[1] <= 1000 for r in ra), "V2", "ration value outside 1..1000")
    E_.check(all(r[2] in (0, 1) for r in ra), "V2", "planted flag not 0/1")
    psum = sum(r[1] for r in ra if r[2] == 1)
    E_.check(r_target > 0 and psum == r_target, "V6",
             f"planted rations add up to {psum}, rations_target is {r_target}")

    # ---------------------------------------------------------------- claims (tier S)
    cl = D["claims"]
    if tier == "S":
        if E_.check(len(cl) == 1, "V5", f"tier S case needs exactly one claims row, found {len(cl)}"):
            cargo, wcnt, wval, drum, topt, cmin = cl[0]
            ks = algos.knapsack(items, cap)
            E_.check(cargo == ks, "V5", f"cargo_opt {cargo} but the optimum is {ks}")
            mc = algos.max_compatible_count(wins)
            E_.check(wcnt == mc, "V5", f"window_count_opt {wcnt} but the optimum is {mc}")
            mv = algos.max_compatible_value(wins)
            E_.check(wval == mv, "V5", f"window_value_opt {wval} but the optimum is {mv}")
            rc = algos.rod_cut(prices)
            E_.check(drum == rc, "V5", f"drum_opt {drum} but the optimum is {rc}")
            if ns <= 12:
                hk = algos.held_karp(pts)
                E_.check(topt == hk, "V5", f"tour_opt {topt} but the shortest tour is {hk}")
            if ok_edges:
                vc = algos.min_vertex_cover(s_nodes, sedges)
                E_.check(cmin == vc, "V5", f"cover_min {cmin} but the minimum cover is {vc}")
    else:
        E_.check(len(cl) == 0, "V3", "claims rows are for tier S only")

    # ---------------------------------------------------------------- V7 signature rules
    cats = Counter(r[1] for r in cr)
    share = lambda cs_: sum(cats[c] for c in cs_)  # noqa: E731
    deg = Counter()
    for (_, u, v, _, _) in rd:
        deg[u] += 1
        deg[v] += 1
    if k <= 45 and V:
        if scen == 1:
            E_.check(22 * V <= 20 * E <= 32 * V, "V7", f"Delta Flood: average degree {2 * E / V:.2f} not in 2.2..3.2")
            E_.check(10 * sum(1 for p in pen if p >= 2) >= 4 * V, "V7", "Delta Flood: < 40% locations with penalty >= 2")
            E_.check(nw >= 3, "V7", "Delta Flood: needs at least 3 waves")
            E_.check(100 * share((0, 1)) >= 55 * n, "V7", "Delta Flood: food+water crates < 55%")
        elif scen == 2:
            E_.check(20 * V <= 20 * E <= 26 * V, "V7", f"Mountain Earthquake: average degree {2 * E / V:.2f} not in 2.0..2.6")
            E_.check(100 * share((2, 3)) >= 45 * n, "V7", "Mountain Earthquake: medicine+tool crates < 45%")
            E_.check(na and 10 * sum(prs) >= 60 * na, "V7", "Mountain Earthquake: mean alarm priority < 6.0")
        elif scen == 3:
            E_.check(4 * types.count("S") >= V, "V7", "Coastal Cyclone: < 25% shelters")
            E_.check(nw >= 3, "V7", "Coastal Cyclone: needs at least 3 waves")
            ov = sum(1 for i in range(len(wins)) for j in range(len(wins))
                     if i != j and wins[i][0] < wins[j][1] and wins[j][0] < wins[i][1]) \
                if len(wins) <= 400 else _overlap_fast(wins)
            E_.check(ov >= 2 * len(wins), "V7", f"Coastal Cyclone: windows overlap {ov / max(1, len(wins)):.2f} others on average (< 2)")
            E_.check(len(set(log)) >= 30, "V7", f"Coastal Cyclone: log uses {len(set(log))} symbols (< 30)")
        elif scen == 4:
            E_.check(20 * E >= 35 * V, "V7", f"Urban Flash Flood: average degree {2 * E / V:.2f} < 3.5")
            if tier in ("M", "L") and ticks:
                E_.check(10 * na >= 15 * (ticks[-1] + 1), "V7", "Urban Flash Flood: < 1.5 alarms per tick")
            E_.check(10 * cats[4] >= n, "V7", "Urban Flash Flood: rare crates < 10%")
        elif scen == 5:
            E_.check(20 * E <= 24 * V, "V7", f"Landslide Corridor: average degree {2 * E / V:.2f} > 2.4")
            E_.check(max(deg.values() or [0]) <= 4, "V7", "Landslide Corridor: a location has more than 4 roads")
            if hop is not None and min(hop) >= 0:
                E_.check(max(hop) >= V // 4, "V7", f"Landslide Corridor: farthest location {max(hop)} roads away (< floor(V/4) = {V // 4})")
            E_.check(nw >= 3, "V7", "Landslide Corridor: needs at least 3 waves")
            if road_ok:
                closed = {r for (_, r) in wv}
                reach = algos.bfs(algos.build_adj(V, g, closed), 0)
                E_.check(any(0 <= t < V and reach[t] < 0 for t in targets), "V7",
                         "Landslide Corridor: union of waves leaves every target reachable")
        elif scen == 6:
            E_.check(100 * share((1, 2)) >= 55 * n, "V7", "Outbreak Camp: medicine+water crates < 55%")
            E_.check(2 * sum(1 for r in cr if r[4] <= 300) >= n, "V7", "Outbreak Camp: < half of crates expire by hour 300")
            top = Counter(log).most_common(1)[0][1] if log else 0
            E_.check(4 * top >= len(log), "V7", "Outbreak Camp: no symbol is >= 25% of the log")

    # ---------------------------------------------------------------- V8 traps
    if k == 46:
        def mono(seq_cmp):
            return all(x >= 0 for x in seq_cmp) or all(x <= 0 for x in seq_cmp)
        diffs = lambda col: [cr[i + 1][col] - cr[i][col] for i in range(n - 1)]  # noqa: E731
        vpk = [cr[i + 1][3] * cr[i][2] - cr[i][3] * cr[i + 1][2] for i in range(n - 1)]
        monos = [name for name, d in (("value", diffs(3)), ("weight", diffs(2)), ("expiry", diffs(4)),
                                      ("serial", diffs(5)), ("value-per-kg", vpk)) if mono(d)]
        E_.check(len(monos) >= 3, "V8", f"Dock-order trap: only {monos} are monotone (need 3 of 5)")
    if k == 47:
        opt = algos.knapsack(items, cap)
        gr = algos.greedy_ratio(items, cap)
        E_.check(10 * gr <= 6 * opt, "V8", f"Best-looking-crate trap: greedy {gr} is more than 60% of optimum {opt}")
    if k == 48 and adj is not None and min(hop) >= 0:
        far = max(range(V), key=lambda x: hop[x])
        h2 = algos.bfs(adj, far)
        diam_lb = max(max(hop), max(h2))
        E_.check(diam_lb >= 500, "V8", f"Shortest-looks-cheapest trap: longest distance found {diam_lb} < 500 roads")
        cheap = algos.dijkstra(adj, pen, 0)
        fewest = algos.min_cost_fewest_roads(adj, pen, 0)
        E_.check(any(0 <= t < V and 2 * fewest[t] >= 3 * cheap[t] for t in targets), "V8",
                 "Shortest-looks-cheapest trap: no target whose fewest-roads routes cost >= 1.5x cheapest")
    if k == 49:
        N = len(log)
        run = algos.longest_periodic_run(log, 8)
        E_.check(10 * run >= 9 * N, "V8", f"Near-miss trap: longest repetition of a block <= 8 covers {run}/{N} (< 90%)")
        good = 0
        for (_, p, _) in pt:
            starts = N - len(p) + 1
            if starts > 0 and 2 * algos.kmp_count(log[:N - 1], p[:-1]) >= starts:
                good += 1
        E_.check(good >= 4, "V8", f"Near-miss trap: only {good} patterns near-miss at >= half of start positions")

    # ---------------------------------------------------------------- facts for variety rules
    if tier == "S":
        facts["greedy_suboptimal"][cid] = algos.greedy_ratio(items, cap) < algos.knapsack(items, cap)
        if adj is not None and hop is not None and min(hop) >= 0:
            cheap = algos.dijkstra(adj, pen, 0)
            fewest = algos.min_cost_fewest_roads(adj, pen, 0)
            facts["fewest_dearer"][cid] = any(0 <= t < V and fewest[t] > cheap[t] for t in targets)
    if tier in ("M", "L") and s_vars:
        facts["safety_ratio"][cid] = (m, s_vars)
    for name in MODULE_SHEETS:
        rows = D[name]
        size = len(log) if name == "radio_log" else len(rows)
        if size >= 8:
            key = log if name == "radio_log" else tuple(rows)
            facts["modules"][name].append((hash(key), cid))


def _overlap_fast(wins):
    import bisect
    starts = sorted(w[0] for w in wins)
    fins = sorted(w[1] for w in wins)
    n = len(wins)
    return sum(n - 1 - (n - bisect.bisect_left(starts, f)) - bisect.bisect_right(fins, s) for s, f, _ in wins)


MODULE_SHEETS = ["crates", "locations", "roads", "waves", "radio_log", "radio_patterns", "windows",
                 "incidents", "sites", "tour", "pipeline_dims", "drum_prices", "sensor_edges",
                 "sensor_cover", "safety_rules", "safety_planted", "rations"]


# ====================================================================== driver

def validate(path, subset=False, out=print):
    gerr = Errors()
    try:
        data = read_workbook(path, gerr)
    except Exception as ex:  # unreadable file
        out(f"FILE {path}: cannot be read ({ex})")
        out("RESULT: FAIL")
        return False
    cases = data["cases"]
    ids = [r[0] for r in cases]
    if not subset:
        gerr.check(len(cases) == 50, "V1", f"need exactly 50 cases, found {len(cases)}")
    gerr.check(len(set(ids)) == len(ids), "V1", "case_ids are not distinct")
    seeds = {r[1] for r in cases}
    gerr.check(len(seeds) <= 1, "V1", f"group_seed differs between cases: {sorted(seeds)}")
    seed = cases[0][1] if cases else None
    if not subset:
        gerr.check(sorted(r[2] for r in cases) == list(range(50)), "V1", "case_no must cover 0..49")

    per = defaultdict(lambda: defaultdict(list))
    for name, _ in SHEETS[1:]:
        for row in data[name]:
            per[row[0]][name].append(row[1:])
    unknown = set(per) - set(ids)
    gerr.check(not unknown, "V3", f"rows reference unknown case_ids {sorted(unknown)[:5]}")

    facts = {"greedy_suboptimal": {}, "fewest_dearer": {}, "safety_ratio": {},
             "modules": defaultdict(list)}
    case_ok = 0
    case_lines = []
    for row in cases:
        cid = row[0]
        e = Errors()
        k = row[2]
        if e.check(re.fullmatch(r"\d+-\d\d", cid) is not None and cid == f"{seed}-{k:02d}", "V1",
                   f"case_id {cid!r} must be '<seed>-<two-digit case_no>' = '{seed}-{k:02d}'") \
                and e.check(0 <= k <= 49, "V1", f"case_no {k} not in 0..49"):
            e.check(row[3] == tier_of(k), "V1", f"tier {row[3]!r} but case {k} is tier {tier_of(k)}")
            e.check(row[4] == k % 6 + 1, "V1", f"scenario {row[4]} but case {k} is scenario {k % 6 + 1}")
            try:
                check_case(cid, row[1:], per[cid], e, facts)
            except Exception as ex:
                e.add("V3", f"case data malformed: {type(ex).__name__}: {ex}")
        if e:
            case_lines.append(f"{cid} FAIL")
            for tag, msg in e.items:
                case_lines.append(f"    [{tag}] {msg}")
        else:
            case_lines.append(f"{cid} PASS")
            case_ok += 1

    # variety rules (whole workbook only)
    if not subset:
        gs = facts["greedy_suboptimal"]
        cnt = sum(gs.values())
        gerr.check(cnt >= 5, "V7", f"variety 1: greedy by value/kg not optimal in only {cnt} tier-S cases (need 5)")
        fd = facts["fewest_dearer"]
        cnt2 = sum(fd.values())
        gerr.check(cnt2 >= 5, "V7", f"variety 2: fewest-roads route dearer than cheapest in only {cnt2} tier-S cases (need 5)")
        sr = facts["safety_ratio"]
        gerr.check(len(sr) == 26, "V7", f"variety 3: found {len(sr)} tier M/L cases, expected 26")
        low = sum(1 for m, v in sr.values() if 10 * m < 35 * v)
        mid = sum(1 for m, v in sr.values() if 35 * v <= 10 * m <= 48 * v)
        high = sum(1 for m, v in sr.values() if 10 * m > 48 * v)
        out_ = [c for c, (m, v) in sr.items() if not (25 * v <= 10 * m <= 60 * v)]
        gerr.check(not out_, "V7", f"variety 3: rules per switch outside 2.5..6.0 in {out_}")
        gerr.check(low >= 5 and mid >= 8 and high >= 5, "V7",
                   f"variety 3: bands below 3.5 / 3.5..4.8 / above 4.8 = {low}/{mid}/{high} (need 5/8/5)")
        for name, lst in facts["modules"].items():
            seen = {}
            for h, cid in lst:
                if h in seen:
                    gerr.add("V7", f"variety 4: module {name} of {cid} equals that of {seen[h]}")
                seen[h] = cid
        variety = (f"variety: greedy-suboptimal S cases = {cnt}, fewest-roads-dearer S cases = {cnt2}, "
                   f"safety bands = {low}/{mid}/{high}")
    out(f"LIFELINE validator - file: {os.path.basename(path)} - seed {seed} - "
        f"{'subset mode' if subset else 'full workbook'}")
    if gerr:
        out("WORKBOOK FAIL")
        for tag, msg in gerr.items:
            out(f"    [{tag}] {msg}")
    else:
        out("WORKBOOK PASS (sheets, headers, types, order" + ("" if subset else ", 50 cases, variety rules") + ")")
        if not subset:
            out("    " + variety)
    for line in case_lines:
        out(line)
    ok = not gerr and case_ok == len(cases)
    out(f"SUMMARY: {case_ok}/{len(cases)} cases PASS; workbook {'PASS' if not gerr else 'FAIL'}")
    out(f"RESULT: {'PASS' if ok else 'FAIL'}")
    return ok


def main():
    ap = argparse.ArgumentParser(description="Validate a LIFELINE cases.xlsx")
    ap.add_argument("path")
    ap.add_argument("--subset", action="store_true",
                    help="workbook holds only some cases (skip the 50-case and variety checks)")
    args = ap.parse_args()
    ok = validate(args.path, args.subset)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
