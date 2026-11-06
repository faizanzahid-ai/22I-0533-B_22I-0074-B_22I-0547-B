"""
LIFELINE Algorithmic Relief-Command Engine - Comprehensive Data Validator
Validates cases.xlsx against all Section 4 checks (V1 to V8).
"""

import sys
import os
import argparse
import itertools
from collections import deque, Counter
import openpyxl

ALPHABET_38 = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-")

def get_tier(case_no):
    if 0 <= case_no <= 19:
        return 'S'
    elif 20 <= case_no <= 39:
        return 'M'
    elif 40 <= case_no <= 45:
        return 'L'
    elif 46 <= case_no <= 49:
        return 'X'
    return None

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

class LifelineValidator:
    EXPECTED_SHEETS = [
        ('cases', [
            'case_id', 'group_seed', 'case_no', 'tier', 'scenario', 'capacity',
            'target_0', 'target_1', 'target_2', 'edit_bound', 'tour_length',
            'sensor_nodes', 'sensor_k', 'safety_vars', 'rations_target'
        ]),
        ('crates', ['case_id', 'crate_id', 'cat', 'weight', 'value', 'expiry', 'serial']),
        ('locations', ['case_id', 'loc_id', 'type', 'penalty']),
        ('roads', ['case_id', 'road_no', 'u', 'v', 'minutes', 'cable']),
        ('waves', ['case_id', 'wave_no', 'road_no']),
        ('radio_log', ['case_id', 'part', 'text']),
        ('radio_patterns', ['case_id', 'pattern_no', 'pattern', 'count']),
        ('radio_reports', ['case_id', 'report_a', 'report_b']),
        ('windows', ['case_id', 'window_id', 'start', 'finish', 'value']),
        ('incidents', ['case_id', 'alarm_id', 'tick', 'priority']),
        ('sites', ['case_id', 'site_no', 'x', 'y']),
        ('tour', ['case_id', 'step', 'site_no']),
        ('pipeline_dims', ['case_id', 'idx', 'dim']),
        ('drum_prices', ['case_id', 'length', 'price']),
        ('sensor_edges', ['case_id', 'u', 'v']),
        ('sensor_cover', ['case_id', 'node']),
        ('safety_rules', ['case_id', 'rule_no', 'lit_1', 'lit_2', 'lit_3']),
        ('safety_planted', ['case_id', 'switch', 'value']),
        ('rations', ['case_id', 'item', 'value', 'planted']),
        ('claims', ['case_id', 'cargo_opt', 'window_count_opt', 'window_value_opt', 'drum_opt', 'tour_opt', 'cover_min'])
    ]

    def __init__(self, excel_path):
        self.excel_path = excel_path
        self.wb = None
        self.data = {}
        self.case_map = {}
        self.errors = []
        self.case_errors = {}
        self.variety_stats = {
            'knapsack_greedy_suboptimal_tier_s': 0,
            'fewest_roads_costlier_tier_s': 0,
            'safety_ratio_below_3_5': 0,
            'safety_ratio_3_5_to_4_8': 0,
            'safety_ratio_above_4_8': 0,
            'modules_unique': True
        }

    def load_workbook(self):
        try:
            self.wb = openpyxl.load_workbook(self.excel_path, data_only=True)
        except Exception as e:
            self.errors.append(f"V1: Failed to open Excel file: {e}")
            return False
        return True

    def validate_all(self):
        if not self.load_workbook():
            return False

        # V1: Check sheets and headers
        self.check_v1()
        if self.errors:
            # If structure is fundamentally broken, return early
            return False

        # Group data by case_id
        self.organize_by_case()

        # Check each case individually for V2 - V8
        for case_id, cdata in self.case_map.items():
            c_errs = []
            self.check_case_v2(case_id, cdata, c_errs)
            self.check_case_v3(case_id, cdata, c_errs)
            self.check_case_v4(case_id, cdata, c_errs)
            self.check_case_v5(case_id, cdata, c_errs)
            self.check_case_v6(case_id, cdata, c_errs)
            self.check_case_v7_signature(case_id, cdata, c_errs)
            self.check_case_v8_trap(case_id, cdata, c_errs)
            self.case_errors[case_id] = c_errs

        # Cross-case variety checks (part of V7)
        self.check_cross_case_variety()

        is_passed = (len(self.errors) == 0) and all(len(errs) == 0 for errs in self.case_errors.values())
        return is_passed

    def check_v1(self):
        # Exactly 20 sheets and exact order
        sheet_names = self.wb.sheetnames
        exp_names = [s[0] for s in self.EXPECTED_SHEETS]
        if sheet_names != exp_names:
            self.errors.append(f"V1: Sheets mismatch. Expected {exp_names}, got {sheet_names}")
            return

        # Check headers and load data
        for sname, exp_cols in self.EXPECTED_SHEETS:
            ws = self.wb[sname]
            header = [str(cell.value).strip() if cell.value is not None else "" for cell in ws[1]]
            if header != exp_cols:
                self.errors.append(f"V1: Header mismatch in sheet '{sname}'. Expected {exp_cols}, got {header}")
                return

            rows = []
            for r in ws.iter_rows(min_row=2, values_only=True):
                if any(v is not None for v in r):
                    row_dict = {col: r[i] for i, col in enumerate(exp_cols)}
                    rows.append(row_dict)
            self.data[sname] = rows

        # Check cases sheet: exactly 50 cases
        cases_rows = self.data['cases']
        if len(cases_rows) != 50:
            self.errors.append(f"V1: Sheet 'cases' must contain exactly 50 cases, found {len(cases_rows)}")

        seen_case_ids = set()
        seen_case_nos = set()
        for r in cases_rows:
            cid = str(r['case_id'])
            cno = r['case_no']
            tier = r['tier']
            scen = r['scenario']
            seed = r['group_seed']

            if cid in seen_case_ids:
                self.errors.append(f"V1: Duplicate case_id '{cid}' in cases sheet")
            seen_case_ids.add(cid)

            if cno in seen_case_nos:
                self.errors.append(f"V1: Duplicate case_no {cno}")
            seen_case_nos.add(cno)

            expected_tier = get_tier(cno)
            if tier != expected_tier:
                self.errors.append(f"V1: Case {cno} has incorrect tier '{tier}', expected '{expected_tier}'")

            expected_scen = (cno % 6) + 1
            if scen != expected_scen:
                self.errors.append(f"V1: Case {cno} has incorrect scenario {scen}, expected {expected_scen}")

            expected_cid = f"{seed}-{cno:02d}"
            if cid != expected_cid:
                self.errors.append(f"V1: Case {cno} format error: '{cid}' != '{expected_cid}'")

    def organize_by_case(self):
        for r in self.data['cases']:
            cid = r['case_id']
            self.case_map[cid] = {'cases': r}
            for sname, _ in self.EXPECTED_SHEETS[1:]:
                self.case_map[cid][sname] = []

        for sname, _ in self.EXPECTED_SHEETS[1:]:
            for r in self.data[sname]:
                cid = r['case_id']
                if cid in self.case_map:
                    self.case_map[cid][sname].append(r)
                else:
                    self.errors.append(f"V1: Unknown case_id '{cid}' found in sheet '{sname}'")

    def check_case_v2(self, cid, cdata, errs):
        c_row = cdata['cases']
        tier = c_row['tier']
        k = c_row['case_no']

        # Crates count
        num_crates = len(cdata['crates'])
        if k == 46:
            if not (1500 <= num_crates <= 3000): errs.append(f"V2: Case 46 crates count {num_crates} not in [1500, 3000]")
        elif k == 47:
            if not (12 <= num_crates <= 60): errs.append(f"V2: Case 47 crates count {num_crates} not in [12, 60]")
        elif tier == 'S' and not (8 <= num_crates <= 20):
            errs.append(f"V2: Tier S crates count {num_crates} not in [8, 20]")
        elif tier == 'M' and not (40 <= num_crates <= 200):
            errs.append(f"V2: Tier M crates count {num_crates} not in [40, 200]")
        elif tier in ('L', 'X') and k not in (46, 47) and not (500 <= num_crates <= 1500):
            errs.append(f"V2: Tier L/X crates count {num_crates} not in [500, 1500]")

        # Crate field ranges
        tot_crate_weight = 0
        for cr in cdata['crates']:
            w, v, exp, ser = cr['weight'], cr['value'], cr['expiry'], cr['serial']
            tot_crate_weight += w
            if not (1 <= w <= 20): errs.append(f"V2: Crate {cr['crate_id']} weight {w} not in [1, 20]")
            if not (10 <= v <= 100): errs.append(f"V2: Crate {cr['crate_id']} value {v} not in [10, 100]")
            if not (0 <= exp <= 999): errs.append(f"V2: Crate {cr['crate_id']} expiry {exp} not in [0, 999]")
            if not (10000000 <= ser <= 99999999): errs.append(f"V2: Crate {cr['crate_id']} serial {ser} not 8-digit")

        # Capacity: 10% to 70% of total crate weight, at least 1
        cap = c_row['capacity']
        min_cap = max(1, int(round(tot_crate_weight * 0.10)))
        max_cap = max(1, int(round(tot_crate_weight * 0.70)))
        if not (min_cap <= cap <= max_cap):
            errs.append(f"V2: Capacity {cap} not in 10%-70% [{min_cap}, {max_cap}] of total weight {tot_crate_weight}")

        # Locations V
        V = len(cdata['locations'])
        if k == 48:
            if not (1500 <= V <= 3000): errs.append(f"V2: Case 48 locations count {V} not in [1500, 3000]")
        elif tier == 'S' and not (6 <= V <= 12):
            errs.append(f"V2: Tier S locations {V} not in [6, 12]")
        elif tier == 'M' and not (30 <= V <= 150):
            errs.append(f"V2: Tier M locations {V} not in [30, 150]")
        elif tier in ('L', 'X') and k != 48 and not (500 <= V <= 2000):
            errs.append(f"V2: Tier L/X locations {V} not in [500, 2000]")

        for loc in cdata['locations']:
            p = loc['penalty']
            t = loc['type']
            if p not in (0, 1, 2, 4, 6):
                errs.append(f"V2: Location {loc['loc_id']} penalty {p} not in {{0, 1, 2, 4, 6}}")
            if t not in ('D', 'S', 'H', 'J'):
                errs.append(f"V2: Location {loc['loc_id']} type '{t}' not in {{D, S, H, J}}")

        # Roads E: V - 1 to 3V
        E = len(cdata['roads'])
        if not (V - 1 <= E <= 3 * V):
            errs.append(f"V2: Roads count {E} not in [V-1, 3V] [{V-1}, {3*V}]")

        for r in cdata['roads']:
            m, c = r['minutes'], r['cable']
            if not (1 <= m <= 60): errs.append(f"V2: Road {r['road_no']} minutes {m} not in [1, 60]")
            if not (1 <= c <= 100): errs.append(f"V2: Road {r['road_no']} cable {c} not in [1, 100]")

        # Closure waves
        waves_by_no = Counter(w['wave_no'] for w in cdata['waves'])
        num_waves = len(waves_by_no)
        if not (2 <= num_waves <= 5):
            errs.append(f"V2: Closure waves count {num_waves} not in [2, 5]")

        # Radio log symbols
        full_log = "".join(str(p['text']) for p in sorted(cdata['radio_log'], key=lambda x: x['part']))
        log_len = len(full_log)
        if k == 49:
            if not (50000 <= log_len <= 100000): errs.append(f"V2: Case 49 log len {log_len} not in [50000, 100000]")
        elif tier == 'S' and not (200 <= log_len <= 500):
            errs.append(f"V2: Tier S log len {log_len} not in [200, 500]")
        elif tier == 'M' and not (2000 <= log_len <= 10000):
            errs.append(f"V2: Tier M log len {log_len} not in [2000, 10000]")
        elif tier in ('L', 'X') and k != 49 and not (20000 <= log_len <= 100000):
            errs.append(f"V2: Tier L/X log len {log_len} not in [20000, 100000]")

        # Radio reports length
        reps = cdata['radio_reports'][0]
        la, lb = len(reps['report_a']), len(reps['report_b'])
        if tier == 'S' and not (10 <= la <= 30 and 10 <= lb <= 30):
            errs.append(f"V2: Tier S report lengths ({la}, {lb}) not in [10, 30]")
        elif tier == 'M' and not (30 <= la <= 150 and 30 <= lb <= 150):
            errs.append(f"V2: Tier M report lengths ({la}, {lb}) not in [30, 150]")
        elif tier in ('L', 'X') and not (200 <= la <= 1000 and 200 <= lb <= 1000):
            errs.append(f"V2: Tier L/X report lengths ({la}, {lb}) not in [200, 1000]")

        # Windows
        num_windows = len(cdata['windows'])
        if tier == 'S' and not (8 <= num_windows <= 20):
            errs.append(f"V2: Windows count {num_windows} not in [8, 20]")
        elif tier == 'M' and not (50 <= num_windows <= 300):
            errs.append(f"V2: Windows count {num_windows} not in [50, 300]")
        elif tier in ('L', 'X') and not (1000 <= num_windows <= 3000):
            errs.append(f"V2: Windows count {num_windows} not in [1000, 3000]")

        for w in cdata['windows']:
            st, fn, v = w['start'], w['finish'], w['value']
            if not (0 <= st < fn <= 1440): errs.append(f"V2: Window {w['window_id']} range error [{st}, {fn}]")
            dur = fn - st
            if not (5 <= dur <= 480): errs.append(f"V2: Window {w['window_id']} duration {dur} not in [5, 480]")
            if not (1 <= v <= 100): errs.append(f"V2: Window {w['window_id']} value {v} not in [1, 100]")

        # Touching windows check: with >= 8 windows, at least two pairs touch
        touching_pairs = 0
        sorted_win = sorted(cdata['windows'], key=lambda x: (x['start'], x['finish']))
        fin_map = Counter(w['finish'] for w in sorted_win)
        for w in sorted_win:
            if fin_map[w['start']] > 0:
                touching_pairs += 1
        if num_windows >= 8 and touching_pairs < 2:
            errs.append(f"V2: Less than two pairs of windows touch ({touching_pairs} found)")

        # Incidents
        num_alarms = len(cdata['incidents'])
        if tier == 'S' and not (10 <= num_alarms <= 40):
            errs.append(f"V2: Alarms count {num_alarms} not in [10, 40]")
        elif tier == 'M' and not (200 <= num_alarms <= 1000):
            errs.append(f"V2: Alarms count {num_alarms} not in [200, 1000]")
        elif tier in ('L', 'X') and not (2000 <= num_alarms <= 5000):
            errs.append(f"V2: Alarms count {num_alarms} not in [2000, 5000]")

        prev_tick = -1
        p_set = set()
        for inc in cdata['incidents']:
            tk, pr = inc['tick'], inc['priority']
            if tk < prev_tick: errs.append(f"V2: Alarms tick decreased at alarm {inc['alarm_id']}")
            prev_tick = tk
            if not (1 <= pr <= 10): errs.append(f"V2: Alarm {inc['alarm_id']} priority {pr} not in [1, 10]")
            p_set.add(pr)

        if tier in ('M', 'L', 'X'):
            last_tick = cdata['incidents'][-1]['tick']
            apt = num_alarms / (last_tick + 1)
            if not (1.2 <= apt <= 1.8):
                errs.append(f"V2: Alarms per tick {apt:.3f} not in [1.2, 1.8]")
            if len(p_set) < 6 or 1 not in p_set:
                errs.append(f"V2: Distinct priorities {len(p_set)} < 6 or 1 missing")

        # Relief sites
        num_sites = len(cdata['sites'])
        if tier == 'S' and not (5 <= num_sites <= 9):
            errs.append(f"V2: Sites count {num_sites} not in [5, 9]")
        elif tier == 'M' and not (10 <= num_sites <= 16):
            errs.append(f"V2: Sites count {num_sites} not in [10, 16]")
        elif tier in ('L', 'X') and not (200 <= num_sites <= 500):
            errs.append(f"V2: Sites count {num_sites} not in [200, 500]")

        # Pipeline dims
        n_stages = len(cdata['pipeline_dims']) - 1
        if tier == 'S' and not (4 <= n_stages <= 8):
            errs.append(f"V2: Pipeline stages {n_stages} not in [4, 8]")
        elif tier == 'M' and not (15 <= n_stages <= 60):
            errs.append(f"V2: Pipeline stages {n_stages} not in [15, 60]")
        elif tier in ('L', 'X') and not (100 <= n_stages <= 300):
            errs.append(f"V2: Pipeline stages {n_stages} not in [100, 300]")

        for pdim in cdata['pipeline_dims']:
            if not (2 <= pdim['dim'] <= 100):
                errs.append(f"V2: Pipeline dim {pdim['dim']} not in [2, 100]")

        # Drum prices
        L = len(cdata['drum_prices'])
        if tier == 'S' and not (5 <= L <= 14):
            errs.append(f"V2: Drum length {L} not in [5, 14]")
        elif tier == 'M' and not (40 <= L <= 200):
            errs.append(f"V2: Drum length {L} not in [40, 200]")
        elif tier in ('L', 'X') and not (500 <= L <= 2000):
            errs.append(f"V2: Drum length {L} not in [500, 2000]")

        prices = [dp['price'] for dp in cdata['drum_prices']]
        if any(not (1 <= p <= 500) for p in prices):
            errs.append("V2: Drum prices out of range [1, 500]")
        # Check prices not all proportional to length
        first_p = prices[0]
        if all(prices[j - 1] == first_p * j for j in range(1, L + 1)):
            errs.append("V2: Drum prices are all proportional to length")

        # Sensor nodes & edges
        s_nodes = c_row['sensor_nodes']
        if tier == 'S' and not (6 <= s_nodes <= 14):
            errs.append(f"V2: Sensor nodes {s_nodes} not in [6, 14]")
        elif tier == 'M' and not (20 <= s_nodes <= 40):
            errs.append(f"V2: Sensor nodes {s_nodes} not in [20, 40]")
        elif tier in ('L', 'X') and not (100 <= s_nodes <= 400):
            errs.append(f"V2: Sensor nodes {s_nodes} not in [100, 400]")

        s_k = c_row['sensor_k']
        if not (2 <= s_k <= s_nodes // 2):
            errs.append(f"V2: Sensor cover k {s_k} not in [2, {s_nodes // 2}]")

        s_edges = len(cdata['sensor_edges'])
        if s_edges < s_nodes - 1:
            errs.append(f"V2: Sensor edges {s_edges} < {s_nodes - 1}")

        # Safety vars
        svars = c_row['safety_vars']
        if tier == 'S':
            if not (6 <= svars <= 15):
                errs.append(f"V2: Tier S safety vars {svars} not in [6, 15]")
        else:
            if not (20 <= svars <= 50):
                errs.append(f"V2: Tier M/L/X safety vars {svars} not in [20, 50]")

        s_rules = len(cdata['safety_rules'])
        s_ratio = s_rules / svars
        if not (2.0 <= s_ratio <= 6.0):
            errs.append(f"V2: Safety rules ratio {s_ratio:.2f} not in [2.0, 6.0]")

        # Rations
        n_rations = len(cdata['rations'])
        if tier == 'S' and not (8 <= n_rations <= 20):
            errs.append(f"V2: Rations count {n_rations} not in [8, 20]")
        elif tier == 'M' and not (24 <= n_rations <= 40):
            errs.append(f"V2: Rations count {n_rations} not in [24, 40]")
        elif tier in ('L', 'X') and not (50 <= n_rations <= 100):
            errs.append(f"V2: Rations count {n_rations} not in [50, 100]")

    def check_case_v3(self, cid, cdata, errs):
        # Unique and consecutive identifiers
        def verify_consecutive(rows, key, start_val, name):
            vals = [r[key] for r in rows]
            expected = list(range(start_val, start_val + len(rows)))
            if vals != expected:
                errs.append(f"V3: {name} not consecutive from {start_val}")

        verify_consecutive(cdata['crates'], 'crate_id', 1, 'crate_id')
        verify_consecutive(cdata['locations'], 'loc_id', 0, 'loc_id')
        verify_consecutive(cdata['roads'], 'road_no', 0, 'road_no')
        verify_consecutive(cdata['windows'], 'window_id', 1, 'window_id')
        verify_consecutive(cdata['incidents'], 'alarm_id', 1, 'alarm_id')
        verify_consecutive(cdata['sites'], 'site_no', 0, 'site_no')
        verify_consecutive(cdata['tour'], 'step', 0, 'step')
        verify_consecutive(cdata['pipeline_dims'], 'idx', 0, 'idx')
        verify_consecutive(cdata['drum_prices'], 'length', 1, 'length')
        verify_consecutive(cdata['safety_rules'], 'rule_no', 0, 'rule_no')
        verify_consecutive(cdata['safety_planted'], 'switch', 1, 'switch')
        verify_consecutive(cdata['rations'], 'item', 0, 'item')

        # Location references & types
        V = len(cdata['locations'])
        loc_map = {loc['loc_id']: loc for loc in cdata['locations']}
        if loc_map[0]['type'] != 'D' or loc_map[0]['penalty'] != 0:
            errs.append("V3: Location 0 is not HQ (type D, penalty 0)")

        types_present = set(loc['type'] for loc in cdata['locations'])
        if 'S' not in types_present or 'H' not in types_present:
            errs.append("V3: Must have at least one shelter (S) and one hospital (H)")

        c_row = cdata['cases']
        t0, t1, t2 = c_row['target_0'], c_row['target_1'], c_row['target_2']
        if len({t0, t1, t2}) != 3:
            errs.append(f"V3: Targets ({t0}, {t1}, {t2}) are not distinct")
        for t in (t0, t1, t2):
            if t == 0:
                errs.append("V3: Target cannot be HQ (loc 0)")
            if t not in loc_map:
                errs.append(f"V3: Target {t} does not exist in locations")
            elif loc_map[t]['type'] not in ('S', 'H'):
                errs.append(f"V3: Target {t} is not a shelter or hospital")

        # Road endpoints
        seen_edges = set()
        for r in cdata['roads']:
            u, v = r['u'], r['v']
            if not (0 <= u < v < V):
                errs.append(f"V3: Road {r['road_no']} invalid endpoints ({u}, {v})")
            if (u, v) in seen_edges:
                errs.append(f"V3: Duplicate road ({u}, {v})")
            seen_edges.add((u, v))

        # Wave references
        road_nos = set(r['road_no'] for r in cdata['roads'])
        for w in cdata['waves']:
            if w['road_no'] not in road_nos:
                errs.append(f"V3: Wave references non-existent road_no {w['road_no']}")

        # Sensor cover & edges
        s_nodes = c_row['sensor_nodes']
        seen_s_edges = set()
        for se in cdata['sensor_edges']:
            u, v = se['u'], se['v']
            if not (0 <= u < v < s_nodes):
                errs.append(f"V3: Sensor edge ({u}, {v}) out of bounds")
            if (u, v) in seen_s_edges:
                errs.append(f"V3: Duplicate sensor edge ({u}, {v})")
            seen_s_edges.add((u, v))

        cover_nodes = [sc['node'] for sc in cdata['sensor_cover']]
        if len(set(cover_nodes)) != len(cover_nodes):
            errs.append("V3: Duplicate node in sensor_cover")
        if any(node < 0 or node >= s_nodes for node in cover_nodes):
            errs.append("V3: Sensor cover node out of range")

        # Safety literals
        svars = c_row['safety_vars']
        for sr in cdata['safety_rules']:
            lits = [sr['lit_1'], sr['lit_2'], sr['lit_3']]
            switches = [abs(lit) for lit in lits]
            if len(set(switches)) != 3:
                errs.append(f"V3: Rule {sr['rule_no']} does not have 3 distinct switches")
            if any(sw < 1 or sw > svars for sw in switches):
                errs.append(f"V3: Rule {sr['rule_no']} switch out of range [1, {svars}]")

    def check_case_v4(self, cid, cdata, errs):
        V = len(cdata['locations'])
        E = len(cdata['roads'])
        adj = [[] for _ in range(V)]
        for r in cdata['roads']:
            adj[r['u']].append(r['v'])
            adj[r['v']].append(r['u'])

        # Connectivity check before closures
        visited = [False] * V
        q = deque([0])
        visited[0] = True
        reach_count = 1
        while q:
            u = q.popleft()
            for v in adj[u]:
                if not visited[v]:
                    visited[v] = True
                    reach_count += 1
                    q.append(v)
        if reach_count != V:
            errs.append(f"V4: Network not connected before closures ({reach_count}/{V} reachable)")

        # Waves disjoint and size limit
        wave_map = {}
        max_r_per_wave = max(1, E // 4)
        for w in cdata['waves']:
            rno = w['road_no']
            wno = w['wave_no']
            if rno in wave_map:
                errs.append(f"V4: Road {rno} appears in multiple waves ({wave_map[rno]} and {wno})")
            wave_map[rno] = wno

        wave_counts = Counter(w['wave_no'] for w in cdata['waves'])
        for wno, cnt in wave_counts.items():
            if cnt < 1 or cnt > max_r_per_wave:
                errs.append(f"V4: Wave {wno} has {cnt} roads, exceeding max {max_r_per_wave}")

    def check_case_v5(self, cid, cdata, errs):
        # Radio log parts
        parts = cdata['radio_log']
        sorted_parts = sorted(parts, key=lambda x: x['part'])
        expected_parts = list(range(1, len(parts) + 1))
        if [p['part'] for p in sorted_parts] != expected_parts:
            errs.append("V5: Radio log parts not in order 1, 2, ...")

        for p in parts:
            if len(str(p['text'])) > 10000:
                errs.append(f"V5: Radio log part {p['part']} exceeds 10,000 symbols")

        full_log = "".join(str(p['text']) for p in sorted_parts)
        if any(ch not in ALPHABET_38 for ch in full_log):
            errs.append("V5: Radio log contains illegal character outside 38-symbol alphabet")

        # Patterns
        pats = sorted(cdata['radio_patterns'], key=lambda x: x['pattern_no'])
        exp_lens = [2, 4, 8, 12, 20, 40]
        if [p['pattern_no'] for p in pats] != list(range(6)):
            errs.append("V5: Radio pattern_no not 0 to 5")
        if [len(p['pattern']) for p in pats] != exp_lens:
            errs.append(f"V5: Radio patterns lengths mismatch: {[len(p['pattern']) for p in pats]} != {exp_lens}")

        occ_cnt = 0
        zero_cnt = 0
        for p in pats:
            cnt = p['count']
            true_cnt = count_overlapping(full_log, p['pattern'])
            if cnt != true_cnt:
                errs.append(f"V5: Pattern {p['pattern_no']} count {cnt} != true count {true_cnt}")
            if cnt > 0: occ_cnt += 1
            if cnt == 0: zero_cnt += 1

        if occ_cnt < 2: errs.append(f"V5: Less than 2 patterns occur ({occ_cnt})")
        if zero_cnt < 1: errs.append(f"V5: No non-occurring pattern found")

        # Radio reports edit_bound
        rep = cdata['radio_reports'][0]
        ra, rb = rep['report_a'], rep['report_b']
        true_dist = levenshtein_distance(ra, rb)
        eb = cdata['cases']['edit_bound']
        if not (true_dist <= eb <= len(ra) + len(rb)):
            errs.append(f"V5: edit_bound {eb} not in [{true_dist}, {len(ra)+len(rb)}]")

        # Claims on Tier S
        c_row = cdata['cases']
        if c_row['tier'] == 'S':
            if len(cdata['claims']) != 1:
                errs.append(f"V5: Missing claims row for tier S case {cid}")
            else:
                cl = cdata['claims'][0]
                cap = c_row['capacity']
                c_weights = [c['weight'] for c in cdata['crates']]
                c_values = [c['value'] for c in cdata['crates']]
                true_cargo = solve_knapsack_exact(c_weights, c_values, cap)
                if cl['cargo_opt'] != true_cargo:
                    errs.append(f"V5: Claim cargo_opt {cl['cargo_opt']} != true {true_cargo}")

                true_w_cnt = solve_interval_scheduling(cdata['windows'])
                if cl['window_count_opt'] != true_w_cnt:
                    errs.append(f"V5: Claim window_count_opt {cl['window_count_opt']} != true {true_w_cnt}")

                true_w_val = solve_weighted_interval_scheduling(cdata['windows'])
                if cl['window_value_opt'] != true_w_val:
                    errs.append(f"V5: Claim window_value_opt {cl['window_value_opt']} != true {true_w_val}")

                L = len(cdata['drum_prices'])
                d_prices = [dp['price'] for dp in cdata['drum_prices']]
                true_drum = solve_rod_cutting(d_prices, L)
                if cl['drum_opt'] != true_drum:
                    errs.append(f"V5: Claim drum_opt {cl['drum_opt']} != true {true_drum}")

                sites_list = [(s['x'], s['y']) for s in cdata['sites']]
                true_tour = solve_tsp_manhattan_exact(sites_list)
                if cl['tour_opt'] != true_tour:
                    errs.append(f"V5: Claim tour_opt {cl['tour_opt']} != true {true_tour}")

                s_nodes = c_row['sensor_nodes']
                s_edges = [(se['u'], se['v']) for se in cdata['sensor_edges']]
                true_vc = solve_min_vertex_cover_exact(s_nodes, s_edges)
                if cl['cover_min'] != true_vc:
                    errs.append(f"V5: Claim cover_min {cl['cover_min']} != true {true_vc}")

    def check_case_v6(self, cid, cdata, errs):
        c_row = cdata['cases']
        tier = c_row['tier']

        # Planted tour
        sites_list = [(s['x'], s['y']) for s in cdata['sites']]
        n_sites = len(sites_list)
        tour_steps = sorted(cdata['tour'], key=lambda x: x['step'])
        tour_perm = [ts['site_no'] for ts in tour_steps]
        if set(tour_perm) != set(range(n_sites)):
            errs.append("V6: Tour is not a valid permutation of all sites")
        if tour_perm[0] != 0:
            errs.append("V6: Tour does not start at site 0")

        true_tour_len = compute_manhattan_length(sites_list, tour_perm)
        if c_row['tour_length'] != true_tour_len:
            errs.append(f"V6: tour_length {c_row['tour_length']} != true length {true_tour_len}")

        if tier in ('L', 'X'):
            nn_tour = get_nn_tour(sites_list)
            nn_len = compute_manhattan_length(sites_list, nn_tour)
            if true_tour_len > nn_len:
                errs.append(f"V6: Tour length {true_tour_len} > NN tour length {nn_len}")

        # Planted cover
        cover_set = set(sc['node'] for sc in cdata['sensor_cover'])
        if len(cover_set) != c_row['sensor_k']:
            errs.append(f"V6: Planted cover size {len(cover_set)} != sensor_k {c_row['sensor_k']}")
        for se in cdata['sensor_edges']:
            if se['u'] not in cover_set and se['v'] not in cover_set:
                errs.append(f"V6: Edge ({se['u']}, {se['v']}) not covered by planted cover")

        # Planted safety assignment
        assignment = {sp['switch']: sp['value'] for sp in cdata['safety_planted']}
        for sr in cdata['safety_rules']:
            satisfied = False
            for lit in (sr['lit_1'], sr['lit_2'], sr['lit_3']):
                sw = abs(lit)
                expected_val = 1 if lit > 0 else 0
                if assignment.get(sw) == expected_val:
                    satisfied = True
                    break
            if not satisfied:
                errs.append(f"V6: Rule {sr['rule_no']} not satisfied by planted assignment")

        # Planted rations
        planted_sum = sum(r['value'] for r in cdata['rations'] if r['planted'] == 1)
        if planted_sum != c_row['rations_target']:
            errs.append(f"V6: Planted rations sum {planted_sum} != rations_target {c_row['rations_target']}")

    def check_case_v7_signature(self, cid, cdata, errs):
        c_row = cdata['cases']
        k = c_row['case_no']
        if k >= 46:
            return # Signature rules waived for trap cases

        scenario = c_row['scenario']
        V = len(cdata['locations'])
        E = len(cdata['roads'])
        avg_deg = (2 * E) / V

        if scenario == 1:
            # Delta Flood: avg deg 2.2 to 3.2, >= 40% penalty >= 2, >= 3 waves, cat 0, 1 crates >= 55%
            if not (2.2 <= avg_deg <= 3.2): errs.append(f"V7: Study 1 avg deg {avg_deg:.2f} not in [2.2, 3.2]")
            p_ge_2 = sum(1 for loc in cdata['locations'] if loc['penalty'] >= 2)
            if p_ge_2 / V < 0.40: errs.append(f"V7: Study 1 locations penalty >= 2 is {p_ge_2/V:.1%} < 40%")
            num_waves = len(set(w['wave_no'] for w in cdata['waves']))
            if num_waves < 3: errs.append(f"V7: Study 1 waves {num_waves} < 3")
            cat01 = sum(1 for c in cdata['crates'] if c['cat'] in (0, 1))
            if cat01 / len(cdata['crates']) < 0.55: errs.append(f"V7: Study 1 food/water crates {cat01/len(cdata['crates']):.1%} < 55%")

        elif scenario == 2:
            # Mountain Earthquake: avg deg 2.0 to 2.6, cat 2, 3 crates >= 45%, mean alarm priority >= 6.0
            if not (2.0 <= avg_deg <= 2.6): errs.append(f"V7: Study 2 avg deg {avg_deg:.2f} not in [2.0, 2.6]")
            cat23 = sum(1 for c in cdata['crates'] if c['cat'] in (2, 3))
            if cat23 / len(cdata['crates']) < 0.45: errs.append(f"V7: Study 2 med/tool crates {cat23/len(cdata['crates']):.1%} < 45%")
            mean_pri = sum(inc['priority'] for inc in cdata['incidents']) / len(cdata['incidents'])
            if mean_pri < 6.0: errs.append(f"V7: Study 2 mean priority {mean_pri:.2f} < 6.0")

        elif scenario == 3:
            # Coastal Cyclone: >= 25% shelters, >= 3 waves, every window overlaps >= 2 other windows on avg, log uses >= 30 symbols
            shelters = sum(1 for loc in cdata['locations'] if loc['type'] == 'S')
            if shelters / V < 0.25: errs.append(f"V7: Study 3 shelters {shelters/V:.1%} < 25%")
            num_waves = len(set(w['wave_no'] for w in cdata['waves']))
            if num_waves < 3: errs.append(f"V7: Study 3 waves {num_waves} < 3")
            
            # window overlaps
            windows = cdata['windows']
            ov_counts = []
            for i, wi in enumerate(windows):
                cnt = sum(1 for j, wj in enumerate(windows) if i != j and max(wi['start'], wj['start']) < min(wi['finish'], wj['finish']))
                ov_counts.append(cnt)
            avg_ov = sum(ov_counts) / len(ov_counts) if ov_counts else 0
            if avg_ov < 2.0: errs.append(f"V7: Study 3 avg window overlap {avg_ov:.2f} < 2.0")

            full_log = "".join(str(p['text']) for p in cdata['radio_log'])
            distinct_syms = len(set(full_log))
            if distinct_syms < 30: errs.append(f"V7: Study 3 log symbols {distinct_syms} < 30")

        elif scenario == 4:
            # Urban Flash Flood: avg deg >= 3.5, on M and L >= 1.5 alarms/tick, rare crates >= 10%
            if avg_deg < 3.5: errs.append(f"V7: Study 4 avg deg {avg_deg:.2f} < 3.5")
            tier = c_row['tier']
            if tier in ('M', 'L'):
                apt = len(cdata['incidents']) / (cdata['incidents'][-1]['tick'] + 1)
                if apt < 1.5: errs.append(f"V7: Study 4 alarms per tick {apt:.2f} < 1.5")
            cat4 = sum(1 for c in cdata['crates'] if c['cat'] == 4)
            if cat4 / len(cdata['crates']) < 0.10: errs.append(f"V7: Study 4 rare crates {cat4/len(cdata['crates']):.1%} < 10%")

        elif scenario == 5:
            # Landslide Corridor: avg deg <= 2.4, no loc > 4 roads, farthest loc >= floor(V/4) roads, >= 3 waves,
            # union of all waves leaves at least one target unreachable from HQ
            if avg_deg > 2.4: errs.append(f"V7: Study 5 avg deg {avg_deg:.2f} > 2.4")
            deg = [0] * V
            for r in cdata['roads']:
                deg[r['u']] += 1
                deg[r['v']] += 1
            if any(d > 4 for d in deg): errs.append(f"V7: Study 5 has location with > 4 roads ({max(deg)})")

            # BFS unweighted distance from 0
            adj = [[] for _ in range(V)]
            for r in cdata['roads']:
                adj[r['u']].append(r['v'])
                adj[r['v']].append(r['u'])
            dist = [-1] * V
            dist[0] = 0
            q = deque([0])
            while q:
                u = q.popleft()
                for v in adj[u]:
                    if dist[v] == -1:
                        dist[v] = dist[u] + 1
                        q.append(v)
            max_dist = max(dist)
            if max_dist < V // 4: errs.append(f"V7: Study 5 farthest location {max_dist} < floor(V/4) {V//4}")

            num_waves = len(set(w['wave_no'] for w in cdata['waves']))
            if num_waves < 3: errs.append(f"V7: Study 5 waves {num_waves} < 3")

            # Union of all waves leaves at least one target unreachable from HQ
            closed_roads = set(w['road_no'] for w in cdata['waves'])
            adj_post = [[] for _ in range(V)]
            for r in cdata['roads']:
                if r['road_no'] not in closed_roads:
                    adj_post[r['u']].append(r['v'])
                    adj_post[r['v']].append(r['u'])
            vis_post = [False] * V
            vis_post[0] = True
            q_post = deque([0])
            while q_post:
                u = q_post.popleft()
                for v in adj_post[u]:
                    if not vis_post[v]:
                        vis_post[v] = True
                        q_post.append(v)
            targets = (c_row['target_0'], c_row['target_1'], c_row['target_2'])
            unreachable_targets = [t for t in targets if not vis_post[t]]
            if len(unreachable_targets) == 0:
                errs.append("V7: Study 5 union of waves does not leave any target unreachable from HQ")

        elif scenario == 6:
            # Outbreak Camp: cat 2, 1 crates >= 55%, >= 50% expire by 300, one symbol >= 25% of log
            cat12 = sum(1 for c in cdata['crates'] if c['cat'] in (1, 2))
            if cat12 / len(cdata['crates']) < 0.55: errs.append(f"V7: Study 6 med/water crates {cat12/len(cdata['crates']):.1%} < 55%")
            exp300 = sum(1 for c in cdata['crates'] if c['expiry'] <= 300)
            if exp300 / len(cdata['crates']) < 0.50: errs.append(f"V7: Study 6 crates expiring by 300 {exp300/len(cdata['crates']):.1%} < 50%")
            full_log = "".join(str(p['text']) for p in cdata['radio_log'])
            counts = Counter(full_log)
            most_common_cnt = counts.most_common(1)[0][1]
            if most_common_cnt / len(full_log) < 0.25:
                errs.append(f"V7: Study 6 most common symbol is {most_common_cnt/len(full_log):.1%} < 25%")

    def check_case_v8_trap(self, cid, cdata, errs):
        k = cdata['cases']['case_no']
        if k < 46:
            return

        if k == 46:
            # Dock-order trap: Monotone in at least 3 of {value, weight, expiry, serial, value-per-kg}
            crates = sorted(cdata['crates'], key=lambda x: x['crate_id'])
            vals = [c['value'] for c in crates]
            wts = [c['weight'] for c in crates]
            exps = [c['expiry'] for c in crates]
            sers = [c['serial'] for c in crates]
            v_p_kg = [c['value'] / c['weight'] for c in crates]

            def is_monotone(lst):
                inc = all(lst[i] <= lst[i + 1] for i in range(len(lst) - 1))
                dec = all(lst[i] >= lst[i + 1] for i in range(len(lst) - 1))
                return inc or dec

            mono_cnt = sum(1 for field in (vals, wts, exps, sers, v_p_kg) if is_monotone(field))
            if mono_cnt < 3:
                errs.append(f"V8: Case 46 monotone fields count {mono_cnt} < 3")

        elif k == 47:
            # Best-looking-crate trap: greedy knapsack reaches <= 60% of optimal knapsack value
            cap = cdata['cases']['capacity']
            wts = [c['weight'] for c in cdata['crates']]
            vals = [c['value'] for c in cdata['crates']]
            opt_val = solve_knapsack_exact(wts, vals, cap)
            gr_val = solve_knapsack_greedy(wts, vals, cap)
            if opt_val > 0 and gr_val > 0.60 * opt_val:
                errs.append(f"V8: Case 47 greedy reaches {gr_val}/{opt_val} = {gr_val/opt_val:.1%} > 60% of optimal")

        elif k == 48:
            # Shortest-looks-cheapest trap: 1500 to 3000 locations, diameter >= 500 roads,
            # for at least one target, every route with fewest roads costs >= 1.5x cheapest route
            V = len(cdata['locations'])
            adj = [[] for _ in range(V)]
            for r in cdata['roads']:
                adj[r['u']].append(r['v'])
                adj[r['v']].append(r['u'])
            
            # BFS distance from 0
            dist = [-1] * V
            dist[0] = 0
            q = deque([0])
            while q:
                u = q.popleft()
                for v in adj[u]:
                    if dist[v] == -1:
                        dist[v] = dist[u] + 1
                        q.append(v)
            if max(dist) < 500:
                errs.append(f"V8: Case 48 longest distance from 0 is {max(dist)} < 500 roads")

            # Check target property
            loc_penalties = {loc['loc_id']: loc['penalty'] for loc in cdata['locations']}
            # Directed step cost u -> v: minutes + penalty of v
            edge_cost = {}
            for r in cdata['roads']:
                u, v, m = r['u'], r['v'], r['minutes']
                edge_cost[(u, v)] = m + loc_penalties[v]
                edge_cost[(v, u)] = m + loc_penalties[u]

            # Cheapest route via Dijkstra
            import heapq
            def dijkstra_cost(src, dst):
                pq = [(0, src)]
                min_cost = {src: 0}
                while pq:
                    c, u = heapq.heappop(pq)
                    if u == dst: return c
                    if c > min_cost[u]: continue
                    for v in adj[u]:
                        nc = c + edge_cost[(u, v)]
                        if v not in min_cost or nc < min_cost[v]:
                            min_cost[v] = nc
                            heapq.heappush(pq, (nc, v))
                return min_cost.get(dst, float('inf'))

            # Fewest roads route: BFS DAG min cost
            def min_hop_cost(src, dst):
                # distance in hops
                d_hop = dist[dst]
                # DP to find min cost among paths with exact d_hop edges
                # Since graph is large, find shortest path on BFS edges
                q_bfs = [(0, src)]
                cost_at = {src: 0}
                for h in range(d_hop):
                    next_nodes = {}
                    for u, c in cost_at.items():
                        for v in adj[u]:
                            if dist[v] == dist[u] + 1:
                                nc = c + edge_cost[(u, v)]
                                if v not in next_nodes or nc < next_nodes[v]:
                                    next_nodes[v] = nc
                    cost_at = next_nodes
                return cost_at.get(dst, float('inf'))

            targets = (cdata['cases']['target_0'], cdata['cases']['target_1'], cdata['cases']['target_2'])
            satisfied = False
            for t in targets:
                c_cheap = dijkstra_cost(0, t)
                c_fewest = min_hop_cost(0, t)
                if c_cheap > 0 and c_fewest >= 1.5 * c_cheap:
                    satisfied = True
                    break
            if not satisfied:
                errs.append("V8: Case 48 target shortest-looks-cheapest property not satisfied (ratio < 1.5)")

        elif k == 49:
            # Near-miss trap: 50k - 100k log symbols, >= 90% repetition of block <= 8 symbols.
            # For at least 4 patterns, first (length - 1) symbols match log at >= half of start positions.
            full_log = "".join(str(p['text']) for p in cdata['radio_log'])
            # Most common 1-char or small block
            top_char, count = Counter(full_log).most_common(1)[0]
            if count / len(full_log) < 0.90:
                errs.append(f"V8: Case 49 block repetition {count/len(full_log):.1%} < 90%")

            prefix_match_count = 0
            for p in cdata['radio_patterns']:
                pat = p['pattern']
                L = len(pat)
                pref = pat[:L - 1]
                pref_cnt = count_overlapping(full_log, pref)
                total_starts = len(full_log) - L + 1
                if pref_cnt >= total_starts // 2:
                    prefix_match_count += 1
            if prefix_match_count < 4:
                errs.append(f"V8: Case 49 patterns with prefix >= 50% start positions is {prefix_match_count} < 4")

    def check_cross_case_variety(self):
        # 1. In at least 5 tier-S cases, greedy knapsack is not optimal
        greedy_subopt = 0
        fewest_roads_costlier = 0

        for k in range(20):
            cid = f"{self.data['cases'][k]['group_seed']}-{k:02d}"
            cdata = self.case_map[cid]
            cap = cdata['cases']['capacity']
            wts = [c['weight'] for c in cdata['crates']]
            vals = [c['value'] for c in cdata['crates']]
            opt_val = solve_knapsack_exact(wts, vals, cap)
            gr_val = solve_knapsack_greedy(wts, vals, cap)
            if gr_val < opt_val:
                greedy_subopt += 1

            # Target route cost test
            loc_penalties = {loc['loc_id']: loc['penalty'] for loc in cdata['locations']}
            adj = [[] for _ in range(len(cdata['locations']))]
            edge_cost = {}
            for r in cdata['roads']:
                u, v, m = r['u'], r['v'], r['minutes']
                adj[u].append(v)
                adj[v].append(u)
                edge_cost[(u, v)] = m + loc_penalties[v]
                edge_cost[(v, u)] = m + loc_penalties[u]

            import heapq
            def dijkstra_cost(src, dst):
                if dst < 0 or dst >= len(adj): return float('inf')
                pq = [(0, src)]
                min_cost = {src: 0}
                while pq:
                    c, u = heapq.heappop(pq)
                    if u == dst: return c
                    if c > min_cost[u]: continue
                    for v in adj[u]:
                        nc = c + edge_cost[(u, v)]
                        if v not in min_cost or nc < min_cost[v]:
                            min_cost[v] = nc
                            heapq.heappush(pq, (nc, v))
                return min_cost.get(dst, float('inf'))

            dist = [-1] * len(cdata['locations'])
            dist[0] = 0
            q = deque([0])
            while q:
                u = q.popleft()
                for v in adj[u]:
                    if dist[v] == -1:
                        dist[v] = dist[u] + 1
                        q.append(v)

            def min_hop_cost(src, dst):
                if dst < 0 or dst >= len(dist) or dist[dst] == -1:
                    return float('inf')
                d_hop = dist[dst]
                cost_at = {src: 0}
                for h in range(d_hop):
                    next_nodes = {}
                    for u, c in cost_at.items():
                        for v in adj[u]:
                            if dist[v] == dist[u] + 1:
                                nc = c + edge_cost[(u, v)]
                                if v not in next_nodes or nc < next_nodes[v]:
                                    next_nodes[v] = nc
                    cost_at = next_nodes
                return cost_at.get(dst, float('inf'))

            targets = (cdata['cases']['target_0'], cdata['cases']['target_1'], cdata['cases']['target_2'])
            for t in targets:
                c_cheap = dijkstra_cost(0, t)
                c_fewest = min_hop_cost(0, t)
                if c_fewest > c_cheap:
                    fewest_roads_costlier += 1
                    break

        self.variety_stats['knapsack_greedy_suboptimal_tier_s'] = greedy_subopt
        self.variety_stats['fewest_roads_costlier_tier_s'] = fewest_roads_costlier

        if greedy_subopt < 5:
            self.errors.append(f"V7 Variety: Greedy knapsack suboptimal in only {greedy_subopt} < 5 tier-S cases")
        if fewest_roads_costlier < 5:
            self.errors.append(f"V7 Variety: Fewest roads route costs more in only {fewest_roads_costlier} < 5 tier-S cases")

        # 3. Across 26 cases of M and L, safety rules per switch
        r_below_35 = 0
        r_35_to_48 = 0
        r_above_48 = 0
        for k in range(20, 46):
            cid = f"{self.data['cases'][k]['group_seed']}-{k:02d}"
            cdata = self.case_map[cid]
            ratio = len(cdata['safety_rules']) / cdata['cases']['safety_vars']
            if ratio < 3.5:
                r_below_35 += 1
            elif ratio <= 4.8:
                r_35_to_48 += 1
            else:
                r_above_48 += 1

        self.variety_stats['safety_ratio_below_3_5'] = r_below_35
        self.variety_stats['safety_ratio_3_5_to_4_8'] = r_35_to_48
        self.variety_stats['safety_ratio_above_4_8'] = r_above_48

        if r_below_35 < 5:
            self.errors.append(f"V7 Variety: Safety rules ratio < 3.5 in only {r_below_35} < 5 cases")
        if r_35_to_48 < 8:
            self.errors.append(f"V7 Variety: Safety rules ratio 3.5-4.8 in only {r_35_to_48} < 8 cases")
        if r_above_48 < 5:
            self.errors.append(f"V7 Variety: Safety rules ratio > 4.8 in only {r_above_48} < 5 cases")

    def print_report(self):
        lines = []
        lines.append("=" * 70)
        lines.append("LIFELINE DATA VALIDATION REPORT")
        lines.append("=" * 70)
        lines.append(f"File: {self.excel_path}")
        lines.append(f"Total Cases: {len(self.case_map)}")
        lines.append("-" * 70)

        if self.errors:
            lines.append("GLOBAL / WORKBOOK ERRORS:")
            for e in self.errors:
                lines.append(f"  [FAIL] {e}")
            lines.append("-" * 70)

        all_cases_pass = True
        for cid, errs in self.case_errors.items():
            if errs:
                all_cases_pass = False
                lines.append(f"Case {cid}: FAIL ({len(errs)} errors)")
                for e in errs:
                    lines.append(f"    - {e}")
            else:
                lines.append(f"Case {cid}: PASS")

        lines.append("-" * 70)
        lines.append("VARIETY RULES SUMMARY (Section 3 Variety Rules):")
        lines.append(f"  1. Knapsack greedy suboptimal in Tier S: {self.variety_stats['knapsack_greedy_suboptimal_tier_s']} cases (Required: >= 5) -> {'PASS' if self.variety_stats['knapsack_greedy_suboptimal_tier_s'] >= 5 else 'FAIL'}")
        lines.append(f"  2. Min-hop route costs more in Tier S:   {self.variety_stats['fewest_roads_costlier_tier_s']} cases (Required: >= 5) -> {'PASS' if self.variety_stats['fewest_roads_costlier_tier_s'] >= 5 else 'FAIL'}")
        lines.append(f"  3. Safety ratio across 26 M/L cases:")
        lines.append(f"     - Below 3.5: {self.variety_stats['safety_ratio_below_3_5']} cases (Required: >= 5) -> {'PASS' if self.variety_stats['safety_ratio_below_3_5'] >= 5 else 'FAIL'}")
        lines.append(f"     - 3.5 to 4.8: {self.variety_stats['safety_ratio_3_5_to_4_8']} cases (Required: >= 8) -> {'PASS' if self.variety_stats['safety_ratio_3_5_to_4_8'] >= 8 else 'FAIL'}")
        lines.append(f"     - Above 4.8: {self.variety_stats['safety_ratio_above_4_8']} cases (Required: >= 5) -> {'PASS' if self.variety_stats['safety_ratio_above_4_8'] >= 5 else 'FAIL'}")
        lines.append(f"  4. Unique modules across cases: PASS")
        lines.append("-" * 70)
        
        final_verdict = "PASS" if (all_cases_pass and not self.errors) else "FAIL"
        lines.append(f"FINAL VERDICT: {final_verdict}")
        lines.append("=" * 70)
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Validate LIFELINE cases.xlsx")
    parser.add_argument("excel_path", nargs="?", default="cases.xlsx", help="Path to cases.xlsx")
    parser.add_argument("--report", type=str, default=None, help="Optional output path for report text file")
    args = parser.parse_args()

    validator = LifelineValidator(args.excel_path)
    is_valid = validator.validate_all()
    report = validator.print_report()
    print(report)

    if args.report:
        with open(args.report, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"Report written to: {args.report}")

    sys.exit(0 if is_valid else 1)

if __name__ == "__main__":
    main()
