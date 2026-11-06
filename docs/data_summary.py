"""Per-case summary of cases.xlsx (data understanding): python docs/data_summary.py cases.xlsx"""
import os
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "validator"))
from validate import read_workbook, Errors  # noqa: E402
import algos  # noqa: E402


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "cases.xlsx"
    d = read_workbook(src, Errors())
    per = defaultdict(lambda: defaultdict(list))
    for name in d:
        if name != "cases":
            for r in d[name]:
                per[r[0]][name].append(r[1:])
    print("case  tier sc crates cap  greedy/opt   V     E   deg  waves   log  syms top%  "
          "windows alarms rate meanP rules/var sensors(k) pattern counts")
    for c in d["cases"]:
        cid, tier, sc = c[0], c[3], c[4]
        P = per[cid]
        V, E = len(P["locations"]), len(P["roads"])
        items = [(r[2], r[3]) for r in P["crates"]]
        cap = c[5]
        ratio = "   -" if cap > 3000 else f"{algos.greedy_ratio(items, cap) / algos.knapsack(items, cap):.2f}"
        log = "".join(r[1] for r in P["radio_log"])
        na = len(P["incidents"])
        T = P["incidents"][-1][1] + 1
        mp = sum(r[2] for r in P["incidents"]) / na
        top = Counter(log).most_common(1)[0][1] / len(log)
        print(f"{cid} {tier}   {sc} {len(items):6d} {cap:5d} {ratio:>6s} {V:9d} {E:5d} {2 * E / V:5.2f} "
              f"{len({r[0] for r in P['waves']}):4d} {len(log):6d} {len(set(log)):4d} {100 * top:4.0f} "
              f"{len(P['windows']):8d} {na:6d} {na / T:4.2f} {mp:5.2f} {len(P['safety_rules']) / c[13]:8.2f} "
              f"{c[11]:5d}({c[12]}) {[r[2] for r in P['radio_patterns']]}")


if __name__ == "__main__":
    main()
