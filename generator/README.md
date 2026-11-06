# LIFELINE Data Generator

This directory contains the automated data generation suite for the LIFELINE Algorithmic Relief-Command Engine.

## Requirements
- Python 3.10+
- `openpyxl`

To install requirements:
```bash
pip install openpyxl
```

## Reproduction Command
To reproduce `cases.xlsx` exactly from the group seed:

```bash
python generator/generate.py --seed 17 --output cases.xlsx
```

*(Replace `17` with your specific group number if needed; all randomness is fully deterministic and derived strictly from `seed` and `case_no`).*
