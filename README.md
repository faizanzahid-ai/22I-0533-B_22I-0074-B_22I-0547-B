# LIFELINE: Algorithmic Relief-Command Engine
## Project Iteration 1: Data Generation, Validation & Algorithm Selection

**Course**: Design and Analysis of Algorithms | BS Data Science & Artificial Intelligence  
**Institution**: National University of Computer and Emerging Sciences (FAST-NUCES), Islamabad Campus  

---

### Group Members
- **Ch Faizan Zahid** (22I-0533, Section B) — [GitHub Profile](https://github.com/faizanzahid-ai)
- **Mohid Abbas** (22I-0074, Section B) — [GitHub Profile](https://github.com/Mohid-Abbas)
- **Fizan Tariq** (22I-0547, Section B) — [GitHub Profile](https://github.com/Fizan-Tariq)

**Group Number / Seed**: `39`  
**GitHub Repository**: [https://github.com/faizanzahid-ai/22I-0533-B_22I-0074-B_22I-0547-B](https://github.com/faizanzahid-ai/22I-0533-B_22I-0074-B_22I-0547-B)

---

### Deliverables Manifest
1. `cases.xlsx`: Master Excel workbook containing exactly 50 cases across all 20 required sheets in exact order. Generated programmatically from group seed 39; zero manual editing.
2. `generator/`:
   - `generate.py`: Python program generating `cases.xlsx` from the group seed.
   - `README.md`: Reproduction documentation with the exact command to recreate `cases.xlsx`.
3. `validator/`:
   - `validate.py`: Independent validator checking `cases.xlsx` against all Section 4 rules (V1 to V8).
   - `generate_tests.py`: Generates broken test cases.
   - `run_validation.py`: Complete test runner validating master data and all broken copies.
   - `tests/`: 10 distinct broken test workbooks (two cases, each broken in 5 different ways).
4. `validation_report.txt`: Output of validator showing PASS for all 50 cases and explicit rejection of all 10 corrupted test workbooks.
5. `proposal.pdf`: Exactly 2-page algorithm-selection report and work division:
   - **Page 1**: Table with one row per chosen module (Modules A to I) detailing problems, candidates with complexity, primary selection vs baseline, and data property justifications.
   - **Page 2**: Work division table detailing each member's contributions and proposed Iteration 2 modules.
6. `approach.md` & `approach.pdf`: 2-page approach note covering:
   - Part 1: From story to numbers (narrative justification for all 6 case studies).
   - Part 2: Planted objects and claims (correctness by construction).
   - Part 3: The four adversarial trap cases (Cases 46 to 49).
   - Part 4: What will be hard in Iteration 2 (computational bottlenecks per study).
7. `members.txt`: Names, roll numbers, sections, and group seed.
8. `repository.txt`: Link to the GitHub repository and collaborator details.

---

### One-Command Reproduction
To reproduce `cases.xlsx` and the full validation suite:

```bash
# 1. Generate master cases.xlsx from group seed 39
python generator/generate.py --seed 39 --output cases.xlsx

# 2. Run comprehensive validation and generate validation_report.txt
python validator/run_validation.py

# 3. Generate proposal.pdf (2 pages)
python proposal_generator.py

# 4. Generate approach.pdf (2 pages)
python approach_generator.py
```
