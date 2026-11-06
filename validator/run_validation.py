"""
Run full validation suite on master cases.xlsx and all broken test copies.
Outputs complete validation_report.txt.
"""

import os
import sys
import glob

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from validator.validate import LifelineValidator

def main():
    report_lines = []
    report_lines.append("=" * 80)
    report_lines.append("LIFELINE ALGORITHMIC RELIEF-COMMAND ENGINE")
    report_lines.append("ITERATION 1: COMPLETE VALIDATION REPORT")
    report_lines.append("=" * 80)
    report_lines.append("")

    # 1. Master dataset validation
    master_path = "cases.xlsx"
    report_lines.append("PART 1: MASTER DATASET VALIDATION (cases.xlsx)")
    report_lines.append("-" * 80)
    if not os.path.exists(master_path):
        report_lines.append(f"ERROR: Master file '{master_path}' not found!")
    else:
        v_master = LifelineValidator(master_path)
        v_master.validate_all()
        report_lines.append(v_master.print_report())

    report_lines.append("\n" + "=" * 80)
    report_lines.append("PART 2: REJECTION OF BROKEN TEST COPIES (validator/tests/)")
    report_lines.append("=" * 80)
    report_lines.append("Requirement: At least two valid cases, each broken in at least 5 different ways.")
    report_lines.append("The validator must detect and reject every corrupted copy.\n")

    test_files = sorted(glob.glob("validator/tests/*.xlsx"))
    if not test_files:
        report_lines.append("No test files found in validator/tests/!")
    else:
        for idx, tpath in enumerate(test_files, 1):
            fname = os.path.basename(tpath)
            report_lines.append("-" * 80)
            report_lines.append(f"TEST CASE {idx}: {fname}")
            report_lines.append("-" * 80)
            v_test = LifelineValidator(tpath)
            passed = v_test.validate_all()
            
            if passed:
                report_lines.append(f"Result: UNEXPECTED PASS (Test copy should have been rejected!)")
            else:
                report_lines.append(f"Result: REJECTED (FAIL) - Broken rules successfully detected!")
                if v_test.errors:
                    report_lines.append("Detected Global Errors:")
                    for err in v_test.errors:
                        report_lines.append(f"  [X] {err}")
                for cid, errs in v_test.case_errors.items():
                    if errs:
                        report_lines.append(f"Detected Case Errors for {cid}:")
                        for err in errs:
                            report_lines.append(f"  [X] {err}")
            report_lines.append("")

    report_lines.append("=" * 80)
    report_lines.append("END OF VALIDATION REPORT")
    report_lines.append("=" * 80)

    full_report = "\n".join(report_lines)
    with open("validation_report.txt", "w", encoding="utf-8") as f:
        f.write(full_report)
    print("Full validation report successfully written to validation_report.txt!")

if __name__ == "__main__":
    main()

