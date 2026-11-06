"""LIFELINE case generator.

    python generator/generate.py --seed 39 --out cases.xlsx

Writes the 50-case workbook.  All randomness comes from the group seed and the case number
(see config.rng_for), so the same command always produces the same file.
"""
import argparse
import os
import sys
import time
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lifeline_gen.config import (tier_of, scenario_of, draw_range, rng_for, PATTERN_LENGTHS)
from lifeline_gen import inventory, network, radio, schedule, planted, claims, traps
from lifeline_gen.workbook import SHEETS, write_workbook

MAX_ATTEMPTS = 400


def safety_buckets(seed):
    """Variety rule 3: 26 tier M/L cases split into rules-per-switch bands."""
    rng = rng_for(seed, -1, "safety-buckets")
    b = ["low"] * 7 + ["mid"] * 11 + ["high"] * 8
    rng.shuffle(b)
    return dict(zip(range(20, 46), b))


BAND = {"low": (2.6, 3.3), "mid": (3.7, 4.6), "high": (5.0, 5.8)}


def in_band(m, v, band):
    if band == "low":
        return 25 * v <= 10 * m < 35 * v
    if band == "mid":
        return 35 * v <= 10 * m <= 48 * v
    return 48 * v < 10 * m <= 60 * v


# ---------------------------------------------------------------- modules of one case

def make_crates(seed, k):
    tier = tier_of(k)
    if k == 46:
        rng = rng_for(seed, k, "crates")
        crates = traps.dock_order_crates(rng, rng.randint(*draw_range(k, "crates")))
        return crates, inventory.choose_capacity(rng, crates)
    if k == 47:
        rng = rng_for(seed, k, "crates")
        return traps.best_looking_crates(rng, rng.randint(*draw_range(k, "crates")))
    for att in range(MAX_ATTEMPTS):
        rng = rng_for(seed, k, "crates", att)
        crates = inventory.gen_crates(rng, rng.randint(*draw_range(k, "crates")), scenario_of(k))
        cap = inventory.choose_capacity(rng, crates)
        # variety rule 1: on even tier-S cases greedy by value/kg must not be optimal
        if tier == "S" and k % 2 == 0:
            if inventory.greedy_by_ratio(crates, cap) >= inventory.knapsack_dp(crates, cap):
                continue
        return crates, cap
    raise RuntimeError(f"crates for case {k}")


def relabel(rng, V, roads, *nodes):
    perm = list(range(1, V))
    rng.shuffle(perm)
    mp = [0] + perm
    out = sorted((min(mp[u], mp[v]), max(mp[u], mp[v]), m, c) for (u, v, m, c) in roads)
    return out, mp, [mp[x] for x in nodes]


def permute_list(lst, mp):
    out = [None] * len(lst)
    for old, val in enumerate(lst):
        out[mp[old]] = val
    return out


def make_network(seed, k):
    tier, sc = tier_of(k), scenario_of(k)
    if k == 48:
        rng = rng_for(seed, k, "network")
        V = rng.randint(*draw_range(k, "V"))
        roads, types, pen, T = traps.shortest_looks_cheapest(rng, V)
        roads, mp, (T,) = relabel(rng, V, roads, T)
        types, pen = permute_list(types, mp), permute_list(pen, mp)
        waves = network.make_waves(rng, len(roads), rng.randint(2, 5))
        sh = [i for i in range(1, V) if types[i] in "SH" and i != T]
        return dict(V=V, roads=roads, types=types, pen=pen, waves=waves,
                    targets=[T] + rng.sample(sh, 2))
    need_v2 = tier == "S" and sc in (1, 3, 4, 6)          # variety rule 2
    for att in range(MAX_ATTEMPTS):
        rng = rng_for(seed, k, "network", att)
        V = rng.randint(*draw_range(k, "V"))
        if sc == 4 and tier == "S":
            V = max(V, 7)
        E = network.choose_E(rng, V, sc)
        lo, hi = network.edge_bounds(V, sc)
        if not lo <= E <= hi:
            continue
        if sc == 5:
            raw = network.build_corridor(rng, V, E)
        else:
            raw = network.build_geographic(rng, V, E, sc)
        roads, _, _ = relabel(rng, V, raw)
        E = len(roads)
        if not lo <= E <= hi:
            continue
        adj = network.adjacency(V, roads)
        hop = network.bfs(adj, 0)
        if min(hop) < 0:
            continue
        if sc == 5:
            deg = Counter()
            for u, v, _, _ in roads:
                deg[u] += 1
                deg[v] += 1
            if max(deg.values()) > 4 or max(hop) < V // 4:
                continue
        types = network.assign_types(rng, V, sc)
        pen = network.assign_penalties(rng, V, sc)
        sh = [i for i in range(1, V) if types[i] in "SH"]
        n_waves = rng.randint(3, 5) if sc in (1, 3, 5) else rng.randint(2, 5)
        first = None
        forced = None
        if sc == 5:
            # a landslide closes a bridge road and cuts a community off from the HQ
            adjr = [[] for _ in range(V)]
            for r, (u, v, _, _) in enumerate(roads):
                adjr[u].append((v, r))
                adjr[v].append((u, r))
            brs = network.bridges(V, adjr)
            rng.shuffle(brs)
            for b in brs:
                reach = network.bfs(network.adjacency(V, roads, {b}), 0)
                cut = [t for t in sh if reach[t] < 0]
                if cut:
                    forced, first = b, rng.choice(cut)
                    break
            if forced is None:
                continue
        waves = network.make_waves(rng, E, n_waves, forced)
        if sc == 5:
            closed = {r for w in waves for r in w}
            if network.bfs(network.adjacency(V, roads, closed), 0)[first] >= 0:
                continue
        if need_v2:
            cheap = network.dijkstra(adj, pen, 0)
            fewest = network.fewest_roads_min_cost(adj, pen, 0)
            good = [t for t in sh if fewest[t] > cheap[t]]
            if not good:
                continue
            first = rng.choice(good)
        if first is None:
            targets = rng.sample(sh, 3)
        else:
            targets = [first] + rng.sample([t for t in sh if t != first], 2)
        return dict(V=V, roads=roads, types=types, pen=pen, waves=waves, targets=targets)
    raise RuntimeError(f"network for case {k}")


def make_radio(seed, k):
    rng = rng_for(seed, k, "radio")
    if k == 49:
        log, pats = traps.near_miss_log(rng, rng.randint(*draw_range(k, "log")))
    else:
        log = radio.gen_log(rng, rng.randint(*draw_range(k, "log")), scenario_of(k))
        pats = radio.gen_patterns(rng, log)
    assert sum(1 for _, c in pats if c > 0) >= 2 and any(c == 0 for _, c in pats)
    assert [len(p) for p, _ in pats] == PATTERN_LENGTHS
    lo, hi = draw_range(k, "report")
    a, b, ops = radio.gen_reports(rng_for(seed, k, "reports"), lo, hi, scenario_of(k))
    return log, pats, (a, b, ops)


def make_windows(seed, k):
    for att in range(MAX_ATTEMPTS):
        rng = rng_for(seed, k, "windows", att)
        n = rng.randint(*draw_range(k, "windows"))
        w = schedule.gen_windows(rng, n, scenario_of(k), tier_of(k))
        if schedule.touching_pairs(w) < 2:
            continue
        if scenario_of(k) == 3 and k <= 45 and schedule.overlap_total(w) < 2 * n:
            continue
        return w
    raise RuntimeError(f"windows for case {k}")


def make_incidents(seed, k):
    sc = scenario_of(k)
    for att in range(MAX_ATTEMPTS):
        rng = rng_for(seed, k, "incidents", att)
        n = rng.randint(*draw_range(k, "alarms"))
        inc = schedule.gen_incidents(rng, n, sc, tier_of(k))
        pr = [p for _, p in inc]
        T = inc[-1][0] + 1
        if len(set(pr)) < 6 or 1 not in pr:
            continue
        if not 12 * T <= 10 * n <= 18 * T:
            continue
        if sc == 4 and 10 * n < 15 * T:
            continue
        if sc == 2 and 10 * sum(pr) < 60 * n:
            continue
        return inc
    raise RuntimeError(f"incidents for case {k}")


def build_case(seed, k, bands):
    tier, sc = tier_of(k), scenario_of(k)
    c = dict(k=k, tier=tier, sc=sc)
    c["crates"], c["capacity"] = make_crates(seed, k)
    c["net"] = make_network(seed, k)
    c["log"], c["patterns"], c["reports"] = make_radio(seed, k)
    c["windows"] = make_windows(seed, k)
    c["incidents"] = make_incidents(seed, k)

    rng = rng_for(seed, k, "sites")
    pts = planted.gen_sites(rng, rng.randint(*draw_range(k, "sites")), sc)
    tour = planted.two_opt(pts, planted.nearest_neighbour_tour(pts), 8 if tier in "SM" else 3)
    c["sites"], c["tour"], c["tour_length"] = pts, tour, planted.tour_length(pts, tour)

    rng = rng_for(seed, k, "pipeline")
    c["dims"] = planted.gen_pipeline(rng, rng.randint(*draw_range(k, "stages")))
    rng = rng_for(seed, k, "drum")
    c["drum"] = planted.gen_drum(rng, rng.randint(*draw_range(k, "drum")))
    rng = rng_for(seed, k, "sensors")
    n = rng.randint(*draw_range(k, "sensors"))
    c["sensor_n"] = n
    c["sensor_k"], c["cover"], c["sensor_edges"] = planted.gen_sensors(rng, n)

    rng = rng_for(seed, k, "safety")
    v = rng.randint(*draw_range(k, "safety"))
    if k in bands:
        while True:
            ratio = rng.uniform(*BAND[bands[k]])
            if in_band(round(ratio * v), v, bands[k]):
                break
    elif tier == "S":
        ratio = rng.uniform(2.3, 5.5)
    else:
        ratio = rng.uniform(3.0, 5.0)
    c["safety_vars"] = v
    c["assign"], c["rules"] = planted.gen_safety(rng, v, ratio)

    rng = rng_for(seed, k, "rations")
    c["rations"], c["rations_planted"], c["rations_target"] = planted.gen_rations(
        rng, rng.randint(*draw_range(k, "rations")))

    if tier == "S":
        cnt, val = claims.window_opts(c["windows"])
        c["claims"] = (claims.cargo_opt(c["crates"], c["capacity"]), cnt, val,
                       claims.drum_opt(c["drum"]), claims.tour_opt(pts),
                       claims.cover_min(n, c["sensor_edges"]))
    return c


# ---------------------------------------------------------------- rows

def case_rows(seed, c, rows):
    cid = f"{seed}-{c['k']:02d}"
    net = c["net"]
    a, b, ops = c["reports"]
    t = net["targets"]
    rows["cases"].append((cid, seed, c["k"], c["tier"], c["sc"], c["capacity"], t[0], t[1], t[2],
                          ops, c["tour_length"], c["sensor_n"], c["sensor_k"], c["safety_vars"],
                          c["rations_target"]))
    for i, (cat, w, v, e, s) in enumerate(c["crates"], 1):
        rows["crates"].append((cid, i, cat, w, v, e, s))
    for i in range(net["V"]):
        rows["locations"].append((cid, i, net["types"][i], net["pen"][i]))
    for r, (u, v, m, cb) in enumerate(net["roads"]):
        rows["roads"].append((cid, r, u, v, m, cb))
    for w, wave in enumerate(net["waves"], 1):
        for r in sorted(wave):
            rows["waves"].append((cid, w, r))
    for p, text in enumerate(radio.split_log(c["log"]), 1):
        rows["radio_log"].append((cid, p, text))
    for i, (p, cnt) in enumerate(c["patterns"]):
        rows["radio_patterns"].append((cid, i, p, cnt))
    rows["radio_reports"].append((cid, a, b))
    for i, (s, f, v) in enumerate(c["windows"], 1):
        rows["windows"].append((cid, i, s, f, v))
    for i, (tk, p) in enumerate(c["incidents"], 1):
        rows["incidents"].append((cid, i, tk, p))
    for i, (x, y) in enumerate(c["sites"]):
        rows["sites"].append((cid, i, x, y))
    for i, s in enumerate(c["tour"]):
        rows["tour"].append((cid, i, s))
    for i, d in enumerate(c["dims"]):
        rows["pipeline_dims"].append((cid, i, d))
    for j, p in enumerate(c["drum"], 1):
        rows["drum_prices"].append((cid, j, p))
    for u, v in c["sensor_edges"]:
        rows["sensor_edges"].append((cid, u, v))
    for node in c["cover"]:
        rows["sensor_cover"].append((cid, node))
    for i, lits in enumerate(c["rules"], 1):
        rows["safety_rules"].append((cid, i, *lits))
    for j, val in enumerate(c["assign"], 1):
        rows["safety_planted"].append((cid, j, val))
    for i, (val, pl) in enumerate(zip(c["rations"], c["rations_planted"])):
        rows["rations"].append((cid, i, val, pl))
    if "claims" in c:
        rows["claims"].append((cid,) + tuple(c["claims"]))


def main():
    ap = argparse.ArgumentParser(description="Generate the LIFELINE cases.xlsx")
    ap.add_argument("--seed", type=int, default=39, help="group seed (group number)")
    ap.add_argument("--out", default="cases.xlsx")
    args = ap.parse_args()
    bands = safety_buckets(args.seed)
    rows = {name: [] for name, _ in SHEETS}
    t0 = time.time()
    for k in range(50):
        c = build_case(args.seed, k, bands)
        case_rows(args.seed, c, rows)
        print(f"case {args.seed}-{k:02d} tier {c['tier']} scenario {c['sc']}: "
              f"{len(c['crates'])} crates, V={c['net']['V']}, E={len(c['net']['roads'])}, "
              f"log={len(c['log'])}, windows={len(c['windows'])}, alarms={len(c['incidents'])}  "
              f"[{time.time() - t0:.1f}s]", flush=True)
    write_workbook(args.out, rows)
    print(f"wrote {args.out} in {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
