"""Write validation_report.txt: the full workbook first, then every test workbook.

    python validator/run_report.py cases.xlsx validation_report.txt
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from validate import validate  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "cases.xlsx"
    dst = sys.argv[2] if len(sys.argv) > 2 else "validation_report.txt"
    lines = []
    out = lines.append
    out("=" * 78)
    out("LIFELINE - validation report (group seed 39)")
    out(f"generated {time.strftime('%Y-%m-%d %H:%M')} by validator/run_report.py")
    out("=" * 78)
    out("")
    out("PART 1 - the submitted workbook")
    out("-" * 78)
    full_ok = validate(src, subset=False, out=out)
    out("")
    out("PART 2 - validator tests (validator/tests/, --subset mode)")
    out("-" * 78)
    tdir = os.path.join(HERE, "tests")
    table = []
    for f in sorted(os.listdir(tdir)):
        if not f.endswith(".xlsx"):
            continue
        expect = f.startswith("valid_")
        out("")
        out(f">>> {f}")
        ok = validate(os.path.join(tdir, f), subset=True, out=out)
        table.append((f, "PASS" if expect else "FAIL", "PASS" if ok else "FAIL", ok == expect))
    out("")
    out("PART 3 - summary")
    out("-" * 78)
    out(f"submitted workbook: {'PASS' if full_ok else 'FAIL'}")
    out(f"{'test file':55s} {'expected':9s} {'got':5s} ok")
    for f, e, g, good in table:
        out(f"{f:55s} {e:9s} {g:5s} {'yes' if good else 'NO'}")
    rejected = sum(1 for f, e, g, good in table if e == "FAIL" and good)
    broken = sum(1 for f, e, *_ in table if e == "FAIL")
    out(f"broken copies rejected: {rejected}/{broken}; valid copies accepted: "
        f"{sum(1 for f, e, g, good in table if e == 'PASS' and good)}/{sum(1 for _, e, *_ in table if e == 'PASS')}")
    with open(dst, "w", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(lines[-len(table) - 6:]))
    sys.exit(0 if full_ok and all(t[3] for t in table) else 1)


if __name__ == "__main__":
    main()
