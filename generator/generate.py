"""
LIFELINE Algorithmic Relief-Command Engine - Data Generator
Iteration 1: Exactly 50 cases across 6 case studies and 4 trap cases.
"""

import sys
import os
import argparse
import random
import string
import itertools
from collections import deque
import openpyxl

ALPHABET_38 = string.ascii_uppercase + string.digits + "_-"

def get_tier(case_no):
    if 0 <= case_no <= 19:
        return 'S'
    elif 20 <= case_no <= 39:
        return 'M'
    elif 40 <= case_no <= 45:
        return 'L'
    elif 46 <= case_no <= 49:
        return 'X'
    raise ValueError(f"Invalid case_no: {case_no}")

def levenshtein_distance(s1, s2):
    m, n = len(s1), len(s2)
    dp = [list(range(n + 1))] + [[i] + [0] * n for i in range(1, m + 1)]
    for i in range(1, m + 1):
        c1 = s1[i - 1]
        row = dp[i]
        prev = dp[i - 1]
        for j in range(1, n + 1):
            cost = 0 if c1 == s2[j - 1] else 1
            row[j] = min(prev[j] + 1, row[j - 1] + 1, prev[j - 1] + cost)
    return dp[m][n]

def count_overlapping(text, pat):
    cnt = 0
    start = 0
    while True:
        pos = text.find(pat, start)
        if pos == -1:
            break
        cnt += 1
        start = pos + 1
    return cnt

def solve_knapsack_exact(weights, values, capacity):
    dp = [0] * (capacity + 1)
    for w, v in zip(weights, values):
        for c in range(capacity, w - 1, -1):
            if dp[c - w] + v > dp[c]:
                dp[c] = dp[c - w] + v
    return dp[capacity]

def solve_knapsack_greedy(weights, values, capacity):
    items = sorted(enumerate(zip(weights, values)), key=lambda x: (x[1][1] / x[1][0], x[1][1]), reverse=True)
    rem_cap = capacity
    total_val = 0
    for idx, (w, v) in items:
        if w <= rem_cap:
            rem_cap -= w
            total_val += v
    return total_val

def solve_interval_scheduling(windows):
    sorted_w = sorted(windows, key=lambda w: w['finish'])
    count = 0
    last_finish = -1
    for w in sorted_w:
        if w['start'] >= last_finish:
            count += 1
            last_finish = w['finish']
    return count

def solve_weighted_interval_scheduling(windows):
    sorted_w = sorted(windows, key=lambda w: w['finish'])
    n = len(sorted_w)
    if n == 0:
        return 0
    finishes = [w['finish'] for w in sorted_w]
    p = [-1] * n
    for i in range(n):
        s = sorted_w[i]['start']
        low, high, best = 0, i - 1, -1
        while low <= high:
            mid = (low + high) // 2
            if finishes[mid] <= s:
                best = mid
                low = mid + 1
            else:
                high = mid - 1
        p[i] = best
        
    dp = [0] * (n + 1)
    for i in range(1, n + 1):
        val = sorted_w[i - 1]['value']
        prev_idx = p[i - 1]
        include_val = val + (dp[prev_idx + 1] if prev_idx != -1 else 0)
        exclude_val = dp[i - 1]
        dp[i] = max(include_val, exclude_val)
    return dp[n]

def solve_rod_cutting(prices, L):
    dp = [0] * (L + 1)
    for i in range(1, L + 1):
        max_v = 0
        for j in range(1, i + 1):
            max_v = max(max_v, prices[j - 1] + dp[i - j])
        dp[i] = max_v
    return dp[L]

def solve_tsp_manhattan_exact(sites):
    n = len(sites)
    if n <= 1:
        return 0
    dist = [[abs(sites[i][0] - sites[j][0]) + abs(sites[i][1] - sites[j][1]) for j in range(n)] for i in range(n)]
    memo = {(1, 0): 0}
    for size in range(2, n + 1):
        for subset in itertools.combinations(range(1, n), size - 1):
            mask = 1
            for bit in subset:
                mask |= (1 << bit)
            for u in subset:
                prev_mask = mask ^ (1 << u)
                res = float('inf')
                candidates = [0] if prev_mask == 1 else [v for v in subset if v != u]
                for v in candidates:
                    if (prev_mask, v) in memo:
                        res = min(res, memo[(prev_mask, v)] + dist[v][u])
                memo[(mask, u)] = res
    full_mask = (1 << n) - 1
    return min(memo[(full_mask, u)] + dist[u][0] for u in range(1, n))

def solve_min_vertex_cover_exact(n_nodes, edges):
    if not edges:
        return 0
    for k in range(1, n_nodes + 1):
        for cover in itertools.combinations(range(n_nodes), k):
            cover_set = set(cover)
            if all(u in cover_set or v in cover_set for u, v in edges):
                return k
    return n_nodes

def compute_manhattan_length(sites, tour_perm):
    total = 0
    n = len(tour_perm)
    for i in range(n):
        u = tour_perm[i]
        v = tour_perm[(i + 1) % n]
        total += abs(sites[u][0] - sites[v][0]) + abs(sites[u][1] - sites[v][1])
    return total

def get_nn_tour(sites):
    n = len(sites)
    unvisited = set(range(1, n))
    curr = 0
    tour = [0]
    while unvisited:
        nxt = min(unvisited, key=lambda v: abs(sites[curr][0] - sites[v][0]) + abs(sites[curr][1] - sites[v][1]))
        tour.append(nxt)
        unvisited.remove(nxt)
        curr = nxt
    return tour


class LifelineDataGenerator:
    def __init__(self, group_seed):
        self.group_seed = group_seed
        self.cases_data = {
            'cases': [],
            'crates': [],
            'locations': [],
            'roads': [],
            'waves': [],
            'radio_log': [],
            'radio_patterns': [],
            'radio_reports': [],
            'windows': [],
            'incidents': [],
            'sites': [],
            'tour': [],
            'pipeline_dims': [],
            'drum_prices': [],
            'sensor_edges': [],
            'sensor_cover': [],
            'safety_rules': [],
            'safety_planted': [],
            'rations': [],
            'claims': []
        }

    def generate_all(self):
        for k in range(50):
            print(f"Generating case {k:02d}...", end="\r", flush=True)
            self.generate_case(k)
        print("Generated all 50 cases successfully!       ")

    def generate_case(self, k):
        case_rng = random.Random(self.group_seed * 10007 + k * 101 + 42)
        tier = get_tier(k)
        case_id = f"{self.group_seed}-{k:02d}"
        scenario = (k % 6) + 1
        is_trap = (k >= 46)

        # -------------------------------------------------------------
        # 1. CRATES
        # -------------------------------------------------------------
        if k == 46:
            num_crates = case_rng.randint(1500, 3000)
        elif k == 47:
            num_crates = 12 # exactly 12 crates for Case 47
        elif tier == 'S':
            num_crates = case_rng.randint(8, 20)
        elif tier == 'M':
            num_crates = case_rng.randint(40, 200)
        else: # L or X (48, 49)
            num_crates = case_rng.randint(500, 1500)

        start_serial = 10000000 + k * 60000 + case_rng.randint(100, 1000)
        serials = [start_serial + i * 2 for i in range(num_crates)]

        crates = []
        if k == 46:
            # Trap 46: Monotone in at least 3 fields: serial, expiry, weight, value
            for i in range(num_crates):
                cid = i + 1
                cat = case_rng.choice([0, 1, 2, 3, 4])
                w = 1 + int(19 * i / (num_crates - 1))
                exp = int(999 * i / (num_crates - 1))
                v = 10 + int(90 * i / (num_crates - 1))
                crates.append({
                    'case_id': case_id,
                    'crate_id': cid,
                    'cat': cat,
                    'weight': w,
                    'value': v,
                    'expiry': exp,
                    'serial': serials[i]
                })
        elif k == 47:
            # Trap 47: Best-looking-crate trap.
            # 12 crates:
            # Crate 1: weight 1, value 12 (ratio 12.0)
            # Crates 2..5 (4 crates): weight 20, value 100 (ratio 5.0)
            # Crates 6..12 (7 crates): weight 15, value 10 (ratio 0.67)
            # Total weight: 1 + 80 + 105 = 186 kg.
            # Capacity = 20 kg (10.7% of 186 kg, in [10%, 70%]).
            # Greedy takes Crate 1 (wt 1, rem 19), then Crate 6 (wt 15, rem 4).
            # Greedy value = 12 + 10 = 22.
            # Optimal takes Crate 2 (wt 20, val 100).
            # Greedy reaches 22 / 100 = 22% <= 60% of optimal!
            crates.append({
                'case_id': case_id,
                'crate_id': 1,
                'cat': 1,
                'weight': 1,
                'value': 12,
                'expiry': case_rng.randint(0, 999),
                'serial': serials[0]
            })
            for i in range(1, 5):
                crates.append({
                    'case_id': case_id,
                    'crate_id': i + 1,
                    'cat': case_rng.choice([1, 2]),
                    'weight': 20,
                    'value': 100,
                    'expiry': case_rng.randint(0, 999),
                    'serial': serials[i]
                })
            for i in range(5, 12):
                crates.append({
                    'case_id': case_id,
                    'crate_id': i + 1,
                    'cat': case_rng.choice([0, 3, 4]),
                    'weight': 15,
                    'value': 10,
                    'expiry': case_rng.randint(0, 999),
                    'serial': serials[i]
                })
        else:
            for i in range(num_crates):
                cid = i + 1
                ser = serials[i]
                w = case_rng.randint(1, 20)
                v = case_rng.randint(10, 100)
                exp = case_rng.randint(0, 999)
                
                if not is_trap:
                    if scenario == 1:
                        cat = case_rng.choice([0, 1]) if case_rng.random() < 0.70 else case_rng.choice([2, 3, 4])
                    elif scenario == 2:
                        cat = case_rng.choice([2, 3]) if case_rng.random() < 0.65 else case_rng.choice([0, 1, 4])
                    elif scenario == 4:
                        cat = 4 if case_rng.random() < 0.25 else case_rng.choice([0, 1, 2, 3])
                    elif scenario == 6:
                        cat = case_rng.choice([2, 1]) if case_rng.random() < 0.70 else case_rng.choice([0, 3, 4])
                        if case_rng.random() < 0.65:
                            exp = case_rng.randint(0, 290)
                    else:
                        cat = case_rng.choice([0, 1, 2, 3, 4])
                else:
                    cat = case_rng.choice([0, 1, 2, 3, 4])
                    
                crates.append({
                    'case_id': case_id,
                    'crate_id': cid,
                    'cat': cat,
                    'weight': w,
                    'value': v,
                    'expiry': exp,
                    'serial': ser
                })

        # Ensure Variety Rule 1 for Tier S (at least 5 cases, e.g. cases 0 to 7)
        total_crate_weight = sum(c['weight'] for c in crates)
        if k == 47:
            capacity = 20
        elif tier == 'S' and k < 8:
            # Careful construction for greedy suboptimal knapsack:
            # c0: wt 6, val 60 (ratio 10.0)
            # c1: wt 10, val 90 (ratio 9.0)
            # c2: wt 10, val 90 (ratio 9.0)
            # c3..: wt 5, val 10 (ratio 2.0)
            # capacity = 20.
            # Total weight: 6 + 10 + 10 + 5*(num_crates - 3)
            crates[0]['weight'] = 6
            crates[0]['value'] = 60
            crates[1]['weight'] = 10
            crates[1]['value'] = 90
            crates[2]['weight'] = 10
            crates[2]['value'] = 90
            for c in crates[3:]:
                c['weight'] = 5
                c['value'] = 10
            
            # Preserve scenario signature categories:
            if scenario == 1:
                for c in crates[:int(0.65 * len(crates))]:
                    c['cat'] = case_rng.choice([0, 1])
            elif scenario == 2:
                for c in crates[:int(0.65 * len(crates))]:
                    c['cat'] = case_rng.choice([2, 3])
            elif scenario == 6:
                for c in crates[:int(0.65 * len(crates))]:
                    c['cat'] = case_rng.choice([1, 2])
                    c['expiry'] = case_rng.randint(0, 250)

            total_crate_weight = sum(c['weight'] for c in crates)
            capacity = 20 # 20 is around 30% of total_crate_weight, perfectly in [10%, 70%]!
        else:
            # Guarantee signature distributions for non-trap cases
            if not is_trap:
                if scenario == 1:
                    # Food and water >= 55%
                    target_01 = int(0.60 * len(crates)) + 1
                    for c in crates[:target_01]:
                        c['cat'] = case_rng.choice([0, 1])
                elif scenario == 2:
                    # Med & tool >= 45%
                    target_23 = int(0.50 * len(crates)) + 1
                    for c in crates[:target_23]:
                        c['cat'] = case_rng.choice([2, 3])
                elif scenario == 6:
                    # Med & water >= 55%, >= 50% expire by 300
                    target_12 = int(0.60 * len(crates)) + 1
                    for c in crates[:target_12]:
                        c['cat'] = case_rng.choice([1, 2])
                    target_exp = int(0.55 * len(crates)) + 1
                    for c in crates[:target_exp]:
                        c['expiry'] = case_rng.randint(0, 280)

            min_c = max(1, int(round(total_crate_weight * 0.20)))
            max_c = max(min_c, int(round(total_crate_weight * 0.60)))
            capacity = case_rng.randint(min_c, max_c)

        # -------------------------------------------------------------
        # 2. LOCATIONS & ROADS & WAVES
        # -------------------------------------------------------------
        if k == 48:
            V = 1600
        elif tier == 'S':
            V = case_rng.randint(6, 12)
        elif tier == 'M':
            V = case_rng.randint(30, 150)
        else:
            V = case_rng.randint(500, 1000)

        loc_types = ['D'] * V
        loc_penalties = [0] * V
        
        for i in range(1, V):
            p = case_rng.choice([0, 1, 2, 4, 6])
            t = case_rng.choice(['S', 'H', 'J', 'D'])
            if not is_trap:
                if scenario == 1:
                    p = case_rng.choice([2, 4, 6]) if case_rng.random() < 0.60 else case_rng.choice([0, 1])
                elif scenario == 3:
                    t = 'S' if case_rng.random() < 0.40 else case_rng.choice(['H', 'J', 'D'])
            loc_types[i] = t
            loc_penalties[i] = p

        loc_types[1] = 'S'
        loc_types[2] = 'H'
        if V > 3:
            loc_types[3] = 'S'

        # Guarantee Study 1: >= 40% penalty >= 2
        if scenario == 1 and not is_trap:
            num_ge_2 = int(0.48 * V) + 1
            for i in range(1, num_ge_2 + 1):
                loc_penalties[i] = case_rng.choice([2, 4, 6])

        # Guarantee Study 3: >= 25% shelters
        if scenario == 3 and not is_trap:
            num_s = int(0.32 * V) + 1
            for i in range(1, num_s + 1):
                loc_types[i] = 'S'

        # Always guarantee at least one S and at least one H
        loc_types[1] = 'S'
        loc_types[2] = 'H'
        if V > 3:
            loc_types[3] = 'S'

        sh_candidates = [i for i in range(1, V) if loc_types[i] in ('S', 'H')]
        if len(sh_candidates) < 3:
            loc_types[1] = 'S'
            loc_types[2] = 'H'
            if V > 3:
                loc_types[3] = 'S'
            sh_candidates = [i for i in range(1, V) if loc_types[i] in ('S', 'H')]
            
        targets = case_rng.sample(sh_candidates, 3)
        target_0, target_1, target_2 = targets

        locations = []
        for i in range(V):
            locations.append({
                'case_id': case_id,
                'loc_id': i,
                'type': loc_types[i],
                'penalty': loc_penalties[i]
            })

        roads = []
        road_set = set()

        def add_edge(u, v, mins=None, cab=None):
            if u > v:
                u, v = v, u
            if u == v or (u, v) in road_set:
                return False
            road_set.add((u, v))
            m = mins if mins is not None else case_rng.randint(1, 60)
            c = cab if cab is not None else case_rng.randint(1, 100)
            roads.append({
                'case_id': case_id,
                'road_no': len(roads),
                'u': u,
                'v': v,
                'minutes': m,
                'cable': c
            })
            return True

        if k == 48:
            # Trap 48: 1500 to 3000 locations. Longest distance >= 500 roads.
            # Long spine chain: 0 - 1 - 2 - ... - 550.
            # Distance from 0 to 550 is 550 roads >= 500!
            for i in range(550):
                add_edge(i, i + 1, mins=1, cab=case_rng.randint(1, 100))

            # Rest of nodes 551 to V-1: attach to node 0 and each other
            for i in range(551, V):
                parent = case_rng.choice([0, case_rng.randint(551, i - 1) if i > 551 else 0])
                add_edge(parent, i, mins=case_rng.randint(1, 60), cab=case_rng.randint(1, 100))

            # target_0 trap property:
            # target_0 is node 1 (or make target_0 a specific node, say node 551)
            target_0 = 551
            target_1 = 552
            target_2 = 553
            loc_types[target_0] = 'S'
            loc_types[target_1] = 'H'
            loc_types[target_2] = 'S'
            locations[target_0]['type'] = 'S'
            locations[target_1]['type'] = 'H'
            locations[target_2]['type'] = 'S'

            # Fewest roads route: direct road (0, target_0) with minutes = 60, penalty = 6 (cost = 66)
            add_edge(0, target_0, mins=60, cab=50)
            loc_penalties[target_0] = 6
            locations[target_0]['penalty'] = 6
            
            # Alternative route: 0 -> 554 -> target_0 with minutes = 1, penalty = 0 (cost = 2)
            w = 554
            loc_penalties[w] = 0
            locations[w]['penalty'] = 0
            add_edge(0, w, mins=1, cab=10)
            add_edge(w, target_0, mins=1, cab=10)

            # Update target in locations sheet list
            targets = [target_0, target_1, target_2]

            # Add more edges among nodes 551..V-1 to satisfy E in [V-1, 3V]
            target_E = int(1.15 * V)
            while len(roads) < target_E:
                u = case_rng.randint(551, V - 1)
                v = case_rng.randint(551, V - 1)
                add_edge(u, v)

        elif scenario == 5 and not is_trap:
            # Study 5: Landslide Corridor
            # avg degree <= 2.4, no loc > 4 roads, farthest loc >= floor(V/4) roads
            chain_len = min(V - 1, max(V // 4 + 2, 1))
            deg = [0] * V
            for i in range(chain_len):
                add_edge(i, i + 1)
                deg[i] += 1
                deg[i + 1] += 1
            for i in range(chain_len + 1, V):
                # pick parent with deg < 4 that is NOT near 0 (to avoid shortcuts)
                min_parent = min(chain_len, max(1, chain_len // 2))
                avail = [p for p in range(min_parent, i) if deg[p] < 4]
                if not avail:
                    avail = [p for p in range(i) if deg[p] < 4]
                p = case_rng.choice(avail)
                add_edge(p, i)
                deg[p] += 1
                deg[i] += 1
        else:
            for i in range(1, V):
                p = case_rng.randint(0, i - 1)
                add_edge(p, i)

            if not is_trap:
                if scenario == 1:
                    target_E = int(1.3 * V)
                elif scenario == 2:
                    target_E = int(1.15 * V)
                elif scenario == 4:
                    target_E = int(1.9 * V)
                else:
                    target_E = int(1.3 * V)
            else:
                target_E = int(1.3 * V)
            
            target_E = max(V - 1, min(3 * V, target_E))
            
            attempts = 0
            while len(roads) < target_E and attempts < 10000:
                attempts += 1
                u = case_rng.randint(0, V - 1)
                v = case_rng.randint(0, V - 1)
                add_edge(u, v)

            # Variety Rule 2 for tier S
            if tier == 'S' and k < 8:
                add_edge(0, target_0, mins=60, cab=50)
                for r in roads:
                    if (r['u'] == 0 and r['v'] == target_0) or (r['u'] == target_0 and r['v'] == 0):
                        r['minutes'] = 60
                mid_candidates = [i for i in range(1, V) if i != target_0]
                if mid_candidates:
                    w = mid_candidates[0]
                    loc_penalties[w] = 0
                    locations[w]['penalty'] = 0
                    add_edge(0, w, mins=1, cab=10)
                    add_edge(w, target_0, mins=1, cab=10)
                    for r in roads:
                        if (r['u'] == 0 and r['v'] == w) or (r['u'] == w and r['v'] == 0):
                            r['minutes'] = 1
                        if (r['u'] == w and r['v'] == target_0) or (r['u'] == target_0 and r['v'] == w):
                            r['minutes'] = 1

        roads.sort(key=lambda r: (r['u'], r['v']))
        for idx, r in enumerate(roads):
            r['road_no'] = idx

        E = len(roads)
        max_roads_per_wave = max(1, E // 4)
        
        if not is_trap and scenario in (1, 3, 5):
            num_waves = case_rng.randint(3, 5)
        else:
            num_waves = case_rng.randint(2, 5)

        waves = []
        used_road_nos = set()
        if scenario == 5 and not is_trap:
            incident_to_target = [r['road_no'] for r in roads if r['u'] == target_0 or r['v'] == target_0]
            wave_buckets = [[] for _ in range(num_waves)]
            for idx, rno in enumerate(incident_to_target):
                wave_buckets[idx % num_waves].append(rno)
                used_road_nos.add(rno)
            avail_roads = [r['road_no'] for r in roads if r['road_no'] not in used_road_nos]
            case_rng.shuffle(avail_roads)
            for w_idx in range(num_waves):
                while len(wave_buckets[w_idx]) == 0 and avail_roads:
                    rno = avail_roads.pop()
                    wave_buckets[w_idx].append(rno)
                    used_road_nos.add(rno)
                while len(wave_buckets[w_idx]) < max_roads_per_wave and avail_roads and case_rng.random() < 0.4:
                    rno = avail_roads.pop()
                    wave_buckets[w_idx].append(rno)
                    used_road_nos.add(rno)
            for w_idx, b in enumerate(wave_buckets):
                for rno in b:
                    waves.append({
                        'case_id': case_id,
                        'wave_no': w_idx + 1,
                        'road_no': rno
                    })
        else:
            all_rnos = list(range(E))
            case_rng.shuffle(all_rnos)
            curr = 0
            for w in range(1, num_waves + 1):
                count = case_rng.randint(1, min(max_roads_per_wave, max(1, (E - curr) // (num_waves - w + 1))))
                for _ in range(count):
                    if curr < E:
                        waves.append({
                            'case_id': case_id,
                            'wave_no': w,
                            'road_no': all_rnos[curr]
                        })
                        curr += 1

        # -------------------------------------------------------------
        # 3. RADIO LOG, PATTERNS, REPORTS
        # -------------------------------------------------------------
        if k == 49:
            log_len = case_rng.randint(50000, 60000)
        elif tier == 'S':
            log_len = case_rng.randint(200, 500)
        elif tier == 'M':
            log_len = case_rng.randint(2000, 6000)
        else:
            log_len = case_rng.randint(20000, 40000)

        if k == 49:
            rep_count = int(0.93 * log_len)
            log_chars = ['A'] * rep_count
            for _ in range(log_len - rep_count):
                log_chars.append(case_rng.choice(ALPHABET_38))
            full_log = "".join(log_chars)
        elif scenario == 6 and not is_trap:
            rep_sym = case_rng.choice(ALPHABET_38)
            num_rep = int(0.30 * log_len)
            log_chars = [rep_sym] * num_rep
            for _ in range(log_len - num_rep):
                log_chars.append(case_rng.choice(ALPHABET_38))
            case_rng.shuffle(log_chars)
            full_log = "".join(log_chars)
        elif scenario == 3 and not is_trap:
            chars = list(ALPHABET_38[:34])
            while len(chars) < log_len:
                chars.append(case_rng.choice(ALPHABET_38))
            case_rng.shuffle(chars)
            full_log = "".join(chars)
        else:
            full_log = "".join(case_rng.choice(ALPHABET_38) for _ in range(log_len))

        radio_log = []
        chunk_size = 9500
        for p_idx, start_pos in enumerate(range(0, len(full_log), chunk_size)):
            radio_log.append({
                'case_id': case_id,
                'part': p_idx + 1,
                'text': full_log[start_pos:start_pos + chunk_size]
            })

        pattern_lens = [2, 4, 8, 12, 20, 40]
        radio_patterns = []

        if k == 49:
            for p_no, L in enumerate(pattern_lens):
                if p_no < 4:
                    pat = 'A' * L
                elif p_no == 4:
                    pat = 'A' * L
                else:
                    pat = 'Z9_X' * 10
                
                cnt = count_overlapping(full_log, pat)
                radio_patterns.append({
                    'case_id': case_id,
                    'pattern_no': p_no,
                    'pattern': pat,
                    'count': cnt
                })
            if radio_patterns[5]['count'] > 0:
                pat = 'Q7_X' * 10
                cnt = count_overlapping(full_log, pat)
                radio_patterns[5] = {'case_id': case_id, 'pattern_no': 5, 'pattern': pat, 'count': cnt}
        else:
            for p_no, L in enumerate(pattern_lens):
                if p_no < 2:
                    start = case_rng.randint(0, len(full_log) - L)
                    pat = full_log[start:start+L]
                elif p_no == 5:
                    pat = "".join(case_rng.choice("XYZ987") for _ in range(L))
                else:
                    if case_rng.random() < 0.5:
                        start = case_rng.randint(0, len(full_log) - L)
                        pat = full_log[start:start+L]
                    else:
                        pat = "".join(case_rng.choice(ALPHABET_38) for _ in range(L))
                
                cnt = count_overlapping(full_log, pat)
                radio_patterns.append({
                    'case_id': case_id,
                    'pattern_no': p_no,
                    'pattern': pat,
                    'count': cnt
                })
            
            occ_count = sum(1 for p in radio_patterns if p['count'] > 0)
            zero_count = sum(1 for p in radio_patterns if p['count'] == 0)
            if occ_count < 2 or zero_count < 1:
                pat0 = full_log[:2]
                radio_patterns[0]['pattern'] = pat0
                radio_patterns[0]['count'] = count_overlapping(full_log, pat0)
                pat1 = full_log[5:9]
                radio_patterns[1]['pattern'] = pat1
                radio_patterns[1]['count'] = count_overlapping(full_log, pat1)
                pat5 = "".join(case_rng.choice("XYZ_") for _ in range(40))
                while pat5 in full_log:
                    pat5 = "".join(case_rng.choice("XYZ_") for _ in range(40))
                radio_patterns[5]['pattern'] = pat5
                radio_patterns[5]['count'] = 0

        # Radio Reports
        if tier == 'S':
            rep_len_a = case_rng.randint(10, 30)
            rep_len_b = case_rng.randint(10, 30)
        elif tier == 'M':
            rep_len_a = case_rng.randint(30, 150)
            rep_len_b = case_rng.randint(30, 150)
        else:
            rep_len_a = case_rng.randint(200, 250)
            rep_len_b = case_rng.randint(200, 250)

        base_str = "".join(case_rng.choice(ALPHABET_38) for _ in range(max(rep_len_a, rep_len_b)))
        rep_a_chars = list(base_str[:rep_len_a])
        rep_b_chars = list(rep_a_chars[:rep_len_b])
        num_mut = case_rng.randint(1, max(2, len(rep_b_chars) // 10))
        for _ in range(num_mut):
            idx = case_rng.randint(0, len(rep_b_chars) - 1)
            rep_b_chars[idx] = case_rng.choice(ALPHABET_38)

        report_a = "".join(rep_a_chars)
        report_b = "".join(rep_b_chars)
        true_edit_dist = levenshtein_distance(report_a, report_b)
        edit_bound = true_edit_dist + case_rng.randint(0, 5)
        edit_bound = min(edit_bound, len(report_a) + len(report_b))

        radio_reports = [{
            'case_id': case_id,
            'report_a': report_a,
            'report_b': report_b
        }]

        # -------------------------------------------------------------
        # 4. RESCUE WINDOWS
        # -------------------------------------------------------------
        if tier == 'S':
            num_windows = case_rng.randint(8, 20)
        elif tier == 'M':
            num_windows = case_rng.randint(50, 300)
        else:
            num_windows = case_rng.randint(1000, 1500)

        windows = []
        if scenario == 3 and not is_trap:
            for wid in range(1, num_windows + 1):
                st = case_rng.randint(100, 600)
                dur = case_rng.randint(250, 480)
                fn = min(1440, st + dur)
                val = case_rng.randint(1, 100)
                windows.append({
                    'case_id': case_id,
                    'window_id': wid,
                    'start': st,
                    'finish': fn,
                    'value': val
                })
        else:
            for wid in range(1, num_windows + 1):
                st = case_rng.randint(0, 1440 - 5)
                dur = case_rng.randint(5, min(480, 1440 - st))
                fn = st + dur
                val = case_rng.randint(1, 100)
                windows.append({
                    'case_id': case_id,
                    'window_id': wid,
                    'start': st,
                    'finish': fn,
                    'value': val
                })

        # Ensure at least two pairs touch
        windows[0]['start'] = 100
        windows[0]['finish'] = 200
        windows[1]['start'] = 200
        windows[1]['finish'] = 350
        
        windows[2]['start'] = 500
        windows[2]['finish'] = 650
        windows[3]['start'] = 650
        windows[3]['finish'] = 800

        if scenario == 3 and not is_trap:
            overlap_counts = []
            for i, wi in enumerate(windows):
                cnt = sum(1 for j, wj in enumerate(windows) if i != j and max(wi['start'], wj['start']) < min(wi['finish'], wj['finish']))
                overlap_counts.append(cnt)
            avg_ov = sum(overlap_counts) / len(overlap_counts)
            if avg_ov < 2.0:
                for w in windows[4:]:
                    w['start'] = 200
                    w['finish'] = 900

        windows.sort(key=lambda w: w['window_id'])

        # -------------------------------------------------------------
        # 5. INCIDENTS (EMERGENCY QUEUE)
        # -------------------------------------------------------------
        if tier == 'S':
            num_alarms = case_rng.randint(10, 40)
        elif tier == 'M':
            num_alarms = case_rng.randint(200, 1000)
        else:
            num_alarms = case_rng.randint(2000, 3000)

        incidents = []
        if tier in ('M', 'L', 'X'):
            target_ratio = 1.65 if (scenario == 4 and not is_trap) else 1.50
            last_tick = max(1, int(round(num_alarms / target_ratio)) - 1)
            ticks = sorted([case_rng.randint(0, last_tick) for _ in range(num_alarms)])
            ticks[0] = 0
            ticks[-1] = last_tick
            
            if scenario == 2 and not is_trap:
                priorities = [1, 5, 6, 7, 8, 9]
                while len(priorities) < num_alarms:
                    priorities.append(case_rng.randint(6, 10))
            else:
                priorities = [1, 2, 3, 4, 5, 6]
                while len(priorities) < num_alarms:
                    priorities.append(case_rng.randint(1, 10))
            case_rng.shuffle(priorities)
            priorities[0] = 1

            for aid in range(1, num_alarms + 1):
                incidents.append({
                    'case_id': case_id,
                    'alarm_id': aid,
                    'tick': ticks[aid - 1],
                    'priority': priorities[aid - 1]
                })
        else:
            curr_tick = 0
            for aid in range(1, num_alarms + 1):
                if case_rng.random() < 0.6:
                    curr_tick += 1
                p = case_rng.randint(6, 10) if (scenario == 2 and not is_trap) else case_rng.randint(1, 10)
                incidents.append({
                    'case_id': case_id,
                    'alarm_id': aid,
                    'tick': curr_tick,
                    'priority': p
                })
            if scenario == 2 and not is_trap:
                mean_p = sum(inc['priority'] for inc in incidents) / len(incidents)
                if mean_p < 6.0:
                    for inc in incidents:
                        inc['priority'] = max(6, inc['priority'])

        # -------------------------------------------------------------
        # 6. SITES & TOUR (TSP)
        # -------------------------------------------------------------
        if tier == 'S':
            num_sites = case_rng.randint(5, 9)
        elif tier == 'M':
            num_sites = case_rng.randint(10, 16)
        else:
            num_sites = case_rng.randint(200, 300)

        site_coords = set()
        sites = []
        for sno in range(num_sites):
            while True:
                sx = case_rng.randint(0, 999)
                sy = case_rng.randint(0, 999)
                if (sx, sy) not in site_coords:
                    site_coords.add((sx, sy))
                    sites.append({
                        'case_id': case_id,
                        'site_no': sno,
                        'x': sx,
                        'y': sy
                    })
                    break

        sites_list = [(s['x'], s['y']) for s in sites]
        nn_tour = get_nn_tour(sites_list)
        tour_len = compute_manhattan_length(sites_list, nn_tour)
        planted_tour_perm = nn_tour

        tour_rows = []
        for step, sno in enumerate(planted_tour_perm):
            tour_rows.append({
                'case_id': case_id,
                'step': step,
                'site_no': sno
            })

        # -------------------------------------------------------------
        # 7. PIPELINE DIMS
        # -------------------------------------------------------------
        if tier == 'S':
            num_stages = case_rng.randint(4, 8)
        elif tier == 'M':
            num_stages = case_rng.randint(15, 60)
        else:
            num_stages = case_rng.randint(100, 150)

        pipeline_dims = []
        for idx in range(num_stages + 1):
            dim = case_rng.randint(2, 100)
            pipeline_dims.append({
                'case_id': case_id,
                'idx': idx,
                'dim': dim
            })

        # -------------------------------------------------------------
        # 8. DRUM PRICES
        # -------------------------------------------------------------
        if tier == 'S':
            L = case_rng.randint(5, 14)
        elif tier == 'M':
            L = case_rng.randint(40, 200)
        else:
            L = case_rng.randint(500, 800)

        drum_prices = []
        for j in range(1, L + 1):
            p = min(500, max(1, int(1.5 * j) + case_rng.randint(0, 10)))
            drum_prices.append({
                'case_id': case_id,
                'length': j,
                'price': p
            })
        drum_prices[0]['price'] = 2
        if L > 1:
            drum_prices[1]['price'] = 7

        # -------------------------------------------------------------
        # 9. SENSOR EDGES & COVER
        # -------------------------------------------------------------
        if tier == 'S':
            s_nodes = case_rng.randint(6, 14)
        elif tier == 'M':
            s_nodes = case_rng.randint(20, 40)
        else:
            s_nodes = case_rng.randint(100, 200)

        s_k = case_rng.randint(2, s_nodes // 2)
        planted_cover = sorted(case_rng.sample(range(s_nodes), s_k))
        planted_cover_set = set(planted_cover)

        sensor_edges = []
        s_edge_set = set()

        def add_sensor_edge(u, v):
            if u > v:
                u, v = v, u
            if u == v or (u, v) in s_edge_set:
                return False
            if u not in planted_cover_set and v not in planted_cover_set:
                return False
            s_edge_set.add((u, v))
            sensor_edges.append({
                'case_id': case_id,
                'u': u,
                'v': v
            })
            return True

        non_cover = [node for node in range(s_nodes) if node not in planted_cover_set]
        for nc in non_cover:
            c = case_rng.choice(planted_cover)
            add_sensor_edge(c, nc)

        for idx in range(len(planted_cover) - 1):
            add_sensor_edge(planted_cover[idx], planted_cover[idx + 1])

        attempts = 0
        while len(sensor_edges) < s_nodes + s_k and attempts < 5000:
            attempts += 1
            u = case_rng.choice(planted_cover)
            v = case_rng.randint(0, s_nodes - 1)
            add_sensor_edge(u, v)

        sensor_edges.sort(key=lambda e: (e['u'], e['v']))

        sensor_cover_rows = []
        for node in planted_cover:
            sensor_cover_rows.append({
                'case_id': case_id,
                'node': node
            })

        # -------------------------------------------------------------
        # 10. SAFETY RULES (3-SAT)
        # -------------------------------------------------------------
        if tier == 'S':
            safety_vars = case_rng.randint(6, 15)
        elif tier == 'M':
            safety_vars = case_rng.randint(20, 50)
        else:
            safety_vars = case_rng.randint(20, 50)

        if 20 <= k <= 26:
            ratio = 2.8
        elif 27 <= k <= 37:
            ratio = 4.1
        elif 38 <= k <= 45:
            ratio = 5.2
        else:
            ratio = case_rng.uniform(2.5, 5.5)

        num_rules = int(round(safety_vars * ratio))
        num_rules = max(int(2.1 * safety_vars), min(int(5.9 * safety_vars), num_rules))

        planted_assignment = {sw: case_rng.choice([0, 1]) for sw in range(1, safety_vars + 1)}

        safety_rules = []
        for r_no in range(num_rules):
            switches = case_rng.sample(range(1, safety_vars + 1), 3)
            true_sw = switches[0]
            lit1 = true_sw if planted_assignment[true_sw] == 1 else -true_sw
            lit2 = switches[1] if case_rng.random() < 0.5 else -switches[1]
            lit3 = switches[2] if case_rng.random() < 0.5 else -switches[2]
            
            lits = [lit1, lit2, lit3]
            case_rng.shuffle(lits)
            safety_rules.append({
                'case_id': case_id,
                'rule_no': r_no,
                'lit_1': lits[0],
                'lit_2': lits[1],
                'lit_3': lits[2]
            })

        safety_planted_rows = []
        for sw in range(1, safety_vars + 1):
            safety_planted_rows.append({
                'case_id': case_id,
                'switch': sw,
                'value': planted_assignment[sw]
            })

        # -------------------------------------------------------------
        # 11. RATIONS (SUBSET SUM)
        # -------------------------------------------------------------
        if tier == 'S':
            num_rations = case_rng.randint(8, 20)
        elif tier == 'M':
            num_rations = case_rng.randint(24, 40)
        else:
            num_rations = case_rng.randint(50, 100)

        rations = []
        planted_sum = 0
        num_planted = 0
        for item_no in range(num_rations):
            val = case_rng.randint(1, 1000)
            is_pl = 1 if case_rng.random() < 0.4 else 0
            if is_pl:
                planted_sum += val
                num_planted += 1
            rations.append({
                'case_id': case_id,
                'item': item_no,
                'value': val,
                'planted': is_pl
            })
        if num_planted == 0:
            rations[0]['planted'] = 1
            planted_sum += rations[0]['value']

        rations_target = planted_sum

        # -------------------------------------------------------------
        # 12. CLAIMS (TIER S ONLY)
        # -------------------------------------------------------------
        if tier == 'S':
            c_weights = [c['weight'] for c in crates]
            c_values = [c['value'] for c in crates]
            cargo_opt = solve_knapsack_exact(c_weights, c_values, capacity)
            w_count_opt = solve_interval_scheduling(windows)
            w_value_opt = solve_weighted_interval_scheduling(windows)
            d_prices = [dp['price'] for dp in drum_prices]
            drum_opt = solve_rod_cutting(d_prices, L)
            tour_opt = solve_tsp_manhattan_exact(sites_list)
            cover_min = solve_min_vertex_cover_exact(s_nodes, [(e['u'], e['v']) for e in sensor_edges])

            self.cases_data['claims'].append({
                'case_id': case_id,
                'cargo_opt': cargo_opt,
                'window_count_opt': w_count_opt,
                'window_value_opt': w_value_opt,
                'drum_opt': drum_opt,
                'tour_opt': tour_opt,
                'cover_min': cover_min
            })

        self.cases_data['cases'].append({
            'case_id': case_id,
            'group_seed': self.group_seed,
            'case_no': k,
            'tier': tier,
            'scenario': scenario,
            'capacity': capacity,
            'target_0': target_0,
            'target_1': target_1,
            'target_2': target_2,
            'edit_bound': edit_bound,
            'tour_length': tour_len,
            'sensor_nodes': s_nodes,
            'sensor_k': s_k,
            'safety_vars': safety_vars,
            'rations_target': rations_target
        })

        self.cases_data['crates'].extend(crates)
        self.cases_data['locations'].extend(locations)
        self.cases_data['roads'].extend(roads)
        self.cases_data['waves'].extend(waves)
        self.cases_data['radio_log'].extend(radio_log)
        self.cases_data['radio_patterns'].extend(radio_patterns)
        self.cases_data['radio_reports'].extend(radio_reports)
        self.cases_data['windows'].extend(windows)
        self.cases_data['incidents'].extend(incidents)
        self.cases_data['sites'].extend(sites)
        self.cases_data['tour'].extend(tour_rows)
        self.cases_data['pipeline_dims'].extend(pipeline_dims)
        self.cases_data['drum_prices'].extend(drum_prices)
        self.cases_data['sensor_edges'].extend(sensor_edges)
        self.cases_data['sensor_cover'].extend(sensor_cover_rows)
        self.cases_data['safety_rules'].extend(safety_rules)
        self.cases_data['safety_planted'].extend(safety_planted_rows)
        self.cases_data['rations'].extend(rations)

    def write_excel(self, output_path):
        wb = openpyxl.Workbook()
        wb.remove(wb.active)

        sheet_definitions = [
            ('cases', [
                'case_id', 'group_seed', 'case_no', 'tier', 'scenario', 'capacity',
                'target_0', 'target_1', 'target_2', 'edit_bound', 'tour_length',
                'sensor_nodes', 'sensor_k', 'safety_vars', 'rations_target'
            ]),
            ('crates', [
                'case_id', 'crate_id', 'cat', 'weight', 'value', 'expiry', 'serial'
            ]),
            ('locations', [
                'case_id', 'loc_id', 'type', 'penalty'
            ]),
            ('roads', [
                'case_id', 'road_no', 'u', 'v', 'minutes', 'cable'
            ]),
            ('waves', [
                'case_id', 'wave_no', 'road_no'
            ]),
            ('radio_log', [
                'case_id', 'part', 'text'
            ]),
            ('radio_patterns', [
                'case_id', 'pattern_no', 'pattern', 'count'
            ]),
            ('radio_reports', [
                'case_id', 'report_a', 'report_b'
            ]),
            ('windows', [
                'case_id', 'window_id', 'start', 'finish', 'value'
            ]),
            ('incidents', [
                'case_id', 'alarm_id', 'tick', 'priority'
            ]),
            ('sites', [
                'case_id', 'site_no', 'x', 'y'
            ]),
            ('tour', [
                'case_id', 'step', 'site_no'
            ]),
            ('pipeline_dims', [
                'case_id', 'idx', 'dim'
            ]),
            ('drum_prices', [
                'case_id', 'length', 'price'
            ]),
            ('sensor_edges', [
                'case_id', 'u', 'v'
            ]),
            ('sensor_cover', [
                'case_id', 'node'
            ]),
            ('safety_rules', [
                'case_id', 'rule_no', 'lit_1', 'lit_2', 'lit_3'
            ]),
            ('safety_planted', [
                'case_id', 'switch', 'value'
            ]),
            ('rations', [
                'case_id', 'item', 'value', 'planted'
            ]),
            ('claims', [
                'case_id', 'cargo_opt', 'window_count_opt', 'window_value_opt', 'drum_opt', 'tour_opt', 'cover_min'
            ])
        ]

        print("Writing data to Excel sheets...")
        for sname, cols in sheet_definitions:
            ws = wb.create_sheet(title=sname)
            ws.append(cols)
            
            rows = self.cases_data[sname]
            col2 = cols[1]
            rows.sort(key=lambda r: (r['case_id'], r[col2]))

            for r in rows:
                row_vals = []
                for c in cols:
                    val = r[c]
                    if isinstance(val, (int, float)):
                        val = int(val)
                    else:
                        val = str(val)
                    row_vals.append(val)
                ws.append(row_vals)

        wb.save(output_path)
        print(f"Workbook successfully saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate LIFELINE cases.xlsx")
    parser.add_argument("--seed", type=int, default=17, help="Group seed number (default: 17)")
    parser.add_argument("--output", type=str, default="cases.xlsx", help="Output path for cases.xlsx")
    args = parser.parse_args()

    print(f"Generating 50 cases with group seed {args.seed}...")
    generator = LifelineDataGenerator(args.seed)
    generator.generate_all()
    generator.write_excel(args.output)
    print("Done!")

if __name__ == "__main__":
    main()
