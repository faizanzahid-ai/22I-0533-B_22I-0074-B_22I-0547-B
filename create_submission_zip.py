"""
Create submission ZIP archive conforming to LIFELINE Iteration 1 rules.
Naming: RollNoSection1_RollNoSection2_RollNoSection3.zip
"""

import os
import zipfile

def create_zip(zip_name="22I-0533-A_22I-3106-A_22I-3107-A.zip"):
    items_to_include = [
        "cases.xlsx",
        "validation_report.txt",
        "approach.md",
        "approach.pdf",
        "proposal.pdf",
        "repository.txt",
        "members.txt",
        "README.md",
        "generator",
        "validator"
    ]

    with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as zf:
        for item in items_to_include:
            if os.path.isfile(item):
                zf.write(item, arcname=item)
                print(f"Added file: {item}")
            elif os.path.isdir(item):
                for root, dirs, files in os.walk(item):
                    # ignore pycache
                    if "__pycache__" in root:
                        continue
                    for f in files:
                        if f.endswith((".pyc", ".pyo")):
                            continue
                        fpath = os.path.join(root, f)
                        arcname = os.path.relpath(fpath, ".")
                        zf.write(fpath, arcname=arcname)
                print(f"Added directory: {item}")

    print(f"\nSuccessfully created submission ZIP: {zip_name} ({os.path.getsize(zip_name):,} bytes)")

if __name__ == "__main__":
    create_zip()
