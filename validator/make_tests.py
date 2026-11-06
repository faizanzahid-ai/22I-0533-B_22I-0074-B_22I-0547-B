"""Build validator/tests/: valid single-case workbooks cut from cases.xlsx, and broken copies.

    python validator/make_tests.py cases.xlsx

Each broken copy has exactly one deliberate defect (named in the file name and in
tests/README.md); the validator must reject every one of them.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from openpyxl import Workbook  # noqa: E402
from openpyxl.cell import WriteOnlyCell  # noqa: E402

from validate import SHEETS, read_workbook, Errors  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
TESTS = os.path.join(HERE, "tests")


def subset(data, cid):
    return {name: [list(r) for r in data[name] if r[0] == cid] for name, _ in SHEETS}


def write(path, d, drop_sheet=None, headers=None):
    wb = Workbook(write_only=True)
    for name, header in SHEETS:
        if name == drop_sheet:
            continue
        ws = wb.create_sheet(name)
        ws.append((headers or {}).get(name, header))
        for row in d[name]:
            out = []
            for v in row:
                if isinstance(v, str):
                    c = WriteOnlyCell(ws, value=v)
                    c.data_type = "s"
                    out.append(c)
                else:
                    out.append(v)
            ws.append(out)
    wb.save(path)


def col(name, column):
    return [h for n, h in SHEETS if n == name][0].index(column)


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "cases.xlsx"
    data = read_workbook(src, Errors())
    os.makedirs(TESTS, exist_ok=True)
    for f in os.listdir(TESTS):
        if f.endswith(".xlsx"):
            os.remove(os.path.join(TESTS, f))
    made = []

    def emit(fname, d, why, **kw):
        write(os.path.join(TESTS, fname), d, **kw)
        made.append((fname, why))

    # ------------------------------------------------------------------ case 39-00 (Delta Flood, tier S)
    cid = data["cases"][0][0]
    base = subset(data, cid)
    emit(f"valid_{cid}.xlsx", base, "valid tier-S Delta Flood case (must PASS)")

    d = subset(data, cid)
    hdr = {"crates": [h if h != "weight" else "kg" for h in SHEETS[1][1]]}
    emit(f"broken_{cid}_01_header_renamed.xlsx", d, "V1: crates header 'weight' renamed to 'kg'", headers=hdr)

    d = subset(data, cid)
    d["crates"][0][col("crates", "weight")] = 25
    emit(f"broken_{cid}_02_weight_out_of_range.xlsx", d, "V2: crate 1 weighs 25 kg (range 1..20)")

    d = subset(data, cid)
    r0 = d["roads"][0]
    d["roads"][1][2], d["roads"][1][3] = r0[2], r0[3]
    emit(f"broken_{cid}_03_repeated_road.xlsx", d, "V3: road 1 repeats the pair of road 0")

    d = subset(data, cid)
    V = len(d["locations"])
    d["locations"].append([cid, V, "J", 0])
    emit(f"broken_{cid}_04_disconnected.xlsx", d, "V4: an extra location with no road (network not connected)")

    d = subset(data, cid)
    d["radio_patterns"][1][col("radio_patterns", "count")] += 1
    emit(f"broken_{cid}_05_pattern_count.xlsx", d, "V5: count of pattern 1 is off by one")

    d = subset(data, cid)
    d["claims"][0][col("claims", "cargo_opt")] += 5
    emit(f"broken_{cid}_06_wrong_claim.xlsx", d, "V5: cargo_opt claim raised by 5")

    d = subset(data, cid)
    d["cases"][0][col("cases", "tour_length")] += 3
    emit(f"broken_{cid}_07_tour_length.xlsx", d, "V6: tour_length does not match the planted tour")

    d = subset(data, cid)
    c = col("crates", "cat")
    for r in d["crates"]:
        if r[c] in (0, 1):
            r[c] = 3
    emit(f"broken_{cid}_08_signature_food_water.xlsx", d, "V7: Delta Flood with no food/water crates")

    d = subset(data, cid)
    d["cases"][0][col("cases", "tier")] = "M"
    emit(f"broken_{cid}_09_wrong_tier.xlsx", d, "V1: case 00 labelled tier M")

    # ------------------------------------------------------------------ case 39-01 (Mountain Earthquake, tier S)
    cid = data["cases"][1][0]
    base = subset(data, cid)
    emit(f"valid_{cid}.xlsx", base, "valid tier-S Mountain Earthquake case (must PASS)")

    d = subset(data, cid)
    w1 = [r for r in d["waves"] if r[1] == 1][0]
    d["waves"].append([cid, 2, w1[2]])
    d["waves"].sort(key=lambda r: (r[1], r[2]))
    emit(f"broken_{cid}_01_waves_overlap.xlsx", d, "V4: a road closed in wave 1 and again in wave 2")

    d = subset(data, cid)
    d["cases"][0][col("cases", "edit_bound")] = 0
    emit(f"broken_{cid}_02_edit_bound.xlsx", d, "V5: edit_bound 0 is below the true edit distance")

    d = subset(data, cid)
    c = col("rations", "planted")
    d["rations"][0][c] = 1 - d["rations"][0][c]
    emit(f"broken_{cid}_03_rations_sum.xlsx", d, "V6: planted ration selection no longer sums to the target")

    d = subset(data, cid)
    d["sensor_cover"].pop()
    emit(f"broken_{cid}_04_cover_missing_node.xlsx", d, "V6: a node removed from the planted sensor cover")

    d = subset(data, cid)
    c = col("safety_planted", "value")
    for r in d["safety_planted"]:
        r[c] = 1 - r[c]
    emit(f"broken_{cid}_05_assignment.xlsx", d, "V6: every planted switch flipped (rules broken)")

    d = subset(data, cid)
    c = col("incidents", "tick")
    d["incidents"][-1][c] = 0
    emit(f"broken_{cid}_06_tick_decreasing.xlsx", d, "V2: the last alarm's tick goes back to 0")

    d = subset(data, cid)
    V = len(d["locations"])
    have = {(r[2], r[3]) for r in d["roads"]}
    nxt = len(d["roads"])
    for u in range(V):
        for v in range(u + 1, V):
            if (u, v) not in have and nxt < int(1.6 * V):
                d["roads"].append([cid, nxt, u, v, 10, 10])
                nxt += 1
    emit(f"broken_{cid}_07_degree_too_high.xlsx", d, "V7: Mountain Earthquake with average degree above 2.6")

    d = subset(data, cid)
    emit(f"broken_{cid}_08_missing_sheet.xlsx", d, "V1: sheet drum_prices missing", drop_sheet="drum_prices")

    d = subset(data, cid)
    t = d["radio_log"][0][2]
    d["radio_log"][0][2] = t[:5] + "a" + t[6:]
    emit(f"broken_{cid}_09_bad_symbol.xlsx", d, "V2: lower-case 'a' in the radio log")

    # ------------------------------------------------------------------ case 39-47 (trap)
    cid = data["cases"][47][0]
    emit(f"valid_{cid}.xlsx", subset(data, cid), "valid Best-looking-crate trap case (must PASS)")
    d = subset(data, cid)
    d["cases"][0][col("cases", "capacity")] = 21
    emit(f"broken_{cid}_01_trap_defused.xlsx", d, "V8: capacity 21 lets greedy reach the optimum")

    with open(os.path.join(TESTS, "README.md"), "w") as fh:
        fh.write("# Validator test workbooks\n\nMade by `python validator/make_tests.py cases.xlsx`. "
                 "Each file holds one case cut from cases.xlsx; broken copies carry exactly one defect.\n"
                 "Run `python validator/validate.py <file> --subset`.\n\n| file | defect |\n|---|---|\n")
        for f, why in made:
            fh.write(f"| {f} | {why} |\n")
    for f, why in made:
        print(f"{f:55s} {why}")


if __name__ == "__main__":
    main()
