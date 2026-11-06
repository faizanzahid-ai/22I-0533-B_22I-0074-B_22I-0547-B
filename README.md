# LIFELINE: Algorithmic Relief-Command Engine

[![Validation Status](https://img.shields.io/badge/Validator-50%2F50%20PASS-brightgreen?style=flat-square)](validation_report.txt)
[![Adversarial Tests](https://img.shields.io/badge/Trap%20Tests-10%2F10%20REJECTED-success?style=flat-square)](validator/tests/)
[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)](https://www.python.org/)
[![Group Seed](https://img.shields.io/badge/Group%20Seed-39-orange?style=flat-square)](#administrative-metadata)
[![License: Academic](https://img.shields.io/badge/Academic%20Project-FAST--NUCES-red?style=flat-square)](https://isb.nu.edu.pk/)

> **Iteration 1 Deliverable**: Synthetic Benchmark Generation, Property-Enforced Validation Engine, Planted Hardness Architecture, and Rigorous Algorithm Selection.

---

## 📌 Executive Summary

**LIFELINE** is an algorithmic relief-command engine designed to solve mission-critical operational challenges in humanitarian disaster response. In extreme disaster scenarios—such as flash floods, alpine earthquakes, coastal cyclones, and disease outbreaks—humanitarian dispatchers face high-dimensional, combinatorial decision problems under strict capacity, temporal, and terrain constraints.

This repository hosts **Iteration 1** of the LIFELINE project:
1. **Automated Synthetic Benchmark Engine (`generator/`)**: Generates exactly 50 parameterized, mathematically consistent relief scenarios across 20 synchronized relational sheets from deterministic seed `39`.
2. **Comprehensive Validation Suite (`validator/`)**: Formally enforces 8 structural and algorithmic invariants (V1–V8), cross-case diversity distributions, and guarantees the rejection of corrupted or malformed inputs.
3. **Adversarial Benchmark Construction (Tier X)**: Specifically engineers pathological corner cases that defeat naive, greedy, and unhedged algorithms (e.g., QuickSort pivot exhaustion, greedy knapsack traps, BFS hop traps, and catastrophic string backtracking).
4. **Algorithmic Selection & Complexity Roadmap (`proposal.pdf`)**: Formulates exact input-output specifications, asymptotic time/space complexities, and justified primary vs. baseline algorithm choices for 9 core computational modules (A through I).

---

## 👥 Administrative Metadata

* **Institution**: National University of Computer and Emerging Sciences (FAST-NUCES), Islamabad Campus
* **Department**: Department of Computer Science & Artificial Intelligence
* **Degree Program**: BS Data Science & Artificial Intelligence
* **Course**: Design and Analysis of Algorithms (CS-2009)
* **Group Number / Seed**: `39`
* **Canonical Repository**: [https://github.com/faizanzahid-ai/22I-0533-B_22I-0074-B_22I-0547-B](https://github.com/faizanzahid-ai/22I-0533-B_22I-0074-B_22I-0547-B)

### 🧑‍💻 Team Members

| Name | Roll Number | Section | GitHub Profile | Primary Responsibilities |
| :--- | :---: | :---: | :--- | :--- |
| **Ch Faizan Zahid** | `22I-0533` | **B** | [@faizanzahid-ai](https://github.com/faizanzahid-ai) | Generator architecture, Knapsack/Claims solver, Graph generation & wave closures, Core validator engine (V1–V5), Modules A, B, H selection |
| **Mohid Abbas** | `22I-0074` | **B** | [@Mohid-Abbas](https://github.com/Mohid-Abbas) | Incident queues, Rescue window scheduling, Radio logs/telemetry generation, Signature & variety checks (V6–V7), Modules C, D, E selection |
| **Fizan Tariq** | `22I-0547` | **B** | [@Fizan-Tariq](https://github.com/Fizan-Tariq) | Spatial site & sensor network topology, Pipeline dimensions, Drum prices, Adversarial trap construction (V8), Packaging, Modules F, G, I selection |

### 🎓 Course Staff Collaborators
* **Ayman Irshad** ([@aymanirshad](https://github.com/aymanirshad)) — Course Staff / Evaluator
* **Mariam Shaiq** ([@mariamshaiq](https://github.com/mariamshaiq)) — Course Staff / Evaluator
* **Rida Zubair** ([@Rida-Zubair](https://github.com/Rida-Zubair)) — Academic Collaborator

---

## 🗂️ Repository Directory Structure

```text
.
├── cases.xlsx                                  # Master dataset: exactly 50 cases across 20 relational sheets
├── validation_report.txt                       # Formal validation report: 50 PASS + 10 test rejections
├── proposal.pdf                                # Exactly 2-page Algorithm Selection Report & Work Division
├── proposal_generator.py                       # Automated ReportLab compiler for proposal.pdf
├── approach.md                                 # Full narrative and mathematical approach documentation
├── approach.pdf                                # Exactly 2-page compiled approach brief
├── members.txt                                 # Standardized group credentials and profile registry
├── repository.txt                              # GitHub repository URL and collaborator manifest
├── README.md                                   # Comprehensive project documentation
├── generator/
│   ├── generate.py                             # Core deterministic benchmark generator (seed-driven)
│   └── README.md                               # Generator CLI and reproduction guidelines
└── validator/
    ├── validate.py                             # Independent 8-layer validation engine (V1 to V8)
    ├── generate_tests.py                       # Generates 10 corrupt workbooks across 2 valid base cases
    ├── run_validation.py                       # Automated testbed executing master & adversarial checks
    └── tests/                                  # 10 adversarial corrupted test workbooks
        ├── caseA_broken_V1_missing_sheet.xlsx
        ├── caseA_broken_V2_crate_weight.xlsx
        ├── caseA_broken_V3_invalid_target.xlsx
        ├── caseA_broken_V4_disconnected_network.xlsx
        ├── caseA_broken_V5_corrupted_claim.xlsx
        ├── caseB_broken_V2_invalid_penalty.xlsx
        ├── caseB_broken_V3_nonconsecutive_crate_id.xlsx
        ├── caseB_broken_V4_overlapping_waves.xlsx
        ├── caseB_broken_V6_invalid_vertex_cover.xlsx
        └── caseB_broken_V7_signature_priority.xlsx
```

---

## 🌐 Narrative Case Studies: From Story to Mathematical Models

The dataset models 6 disaster archetypes, each mapped to concrete topological, probabilistic, and algebraic invariants:

| Archetype | Real-World Scenario | Mathematical & Algorithmic Formulation |
| :--- | :--- | :--- |
| **Study 1: Delta Flood** | Lowland plain inundated by rising water; roads submerge in progressive waves. | Planar connectivity ($2E/V \in [2.2, 3.2]$), $\ge 40\%$ nodes have traversal penalties $p \in \{2, 4, 6\}$, $\ge 3$ dynamic closure waves, inventory skewed $\ge 55\%$ towards food & water. |
| **Study 2: Mountain Earthquake** | Valley settlement with sparse access routes; sudden aftershock casualty surges. | Sparse arterial tree ($2E/V \in [2.0, 2.6]$), heavy priority on trauma medicine & rescue extraction crates ($\ge 45\%$), emergency alarm bursts with mean priority $\ge 6.0$. |
| **Study 3: Coastal Cyclone** | Storm surge hitting coastal towns; dense interval contention; radio static. | Inundation requires $\ge 25\%$ emergency shelters (type `S`), $\ge 3$ closure waves, highly overlapping rescue intervals (mean degree $\ge 2.0$), radio text spans $\ge 30$ symbols. |
| **Study 4: Urban Flash Flood** | Metropolitan grid with dense alternate routes; high-throughput alarm streams. | Dense arterial grid ($2E/V \ge 3.5$), arrival rate $\ge 1.5$ alarms/tick on Tiers M/L, stockpiles guarantee rare engineering tools ($\text{cat } 4 \ge 10\%$). |
| **Study 5: Landslide Corridor** | Single mountain highway along a ravine; rockfalls cut entire valleys off. | Deep linear topology ($2E/V \le 2.4$, max degree $\le 4$), network depth $\ge \lfloor V/4 \rfloor$ hops from HQ, $\ge 3$ road closure waves whose union cuts off target nodes. |
| **Study 6: Outbreak Camp** | High-density relief camp; biological spoilage; repetitive beacon broadcasts. | Hydration & antibiotics prioritized ($\ge 55\%$), severe perishable decay ($\ge 50\%$ crates expire by hour 300), telemetry dominated by repetitive beacon signals ($\ge 25\%$). |

---

## 💣 Adversarial Trap Cases (Tier X: Cases 46 to 49)

Cases 46–49 intentionally target worst-case complexity boundaries of common algorithmic paradigms:

```
┌───────────────────────────────────────────────────────────────────────────────────────┐
│                                ADVERSARIAL TRAP DESIGN                                │
├─────────────────┬──────────────────────┬──────────────────────┬───────────────────────┤
│ Trap Case       │ Targeted Paradigm    │ Pathological Trigger │ Correct Algorithmic   │
│                 │                      │                      │ Defense               │
├─────────────────┼──────────────────────┼──────────────────────┼───────────────────────┤
│ Case 46:        │ Divide-and-Conquer   │ 1,600 crates with    │ Randomized Pivot,     │
│ Dock-Order      │ Sorting (QuickSort)  │ monotonically sorted │ Introsort, or         │
│                 │                      │ attributes           │ MergeSort             │
├─────────────────┼──────────────────────┼──────────────────────┼───────────────────────┤
│ Case 47:        │ Greedy Value-Density │ Bait crate: wt=1,    │ 1D Tabular 0/1        │
│ Best-Looking    │ Heuristic (Knapsack) │ val=12; blocks four  │ Dynamic Programming   │
│                 │                      │ optimal wt=20 crates │                       │
├─────────────────┼──────────────────────┼──────────────────────┼───────────────────────┤
│ Case 48:        │ Breadth-First Search │ 1-hop path costs 66; │ Dijkstra's Algorithm  │
│ Shortest-Looks- │ (Hop-Count Route)    │ 2-hop detour costs 2 │ with Min-Heap Priority│
│ Cheapest        │                      │ (Ratio = 33.0x)      │ Queue                 │
├─────────────────┼──────────────────────┼──────────────────────┼───────────────────────┤
│ Case 49:        │ Naive String Search  │ 55k symbols with 93% │ Knuth-Morris-Pratt    │
│ Near-Miss       │ Sliding Window       │ 'A' repetition and   │ (KMP) Linear Failure  │
│                 │                      │ prefix match of L-1  │ Automaton             │
└─────────────────┴──────────────────────┴──────────────────────┴───────────────────────┘
```

---

## 🧠 Algorithmic Selection Matrix (Modules A – I)

The formal algorithm selections documented in [`proposal.pdf`](proposal.pdf) cover 9 critical decision problems:

| Module | Computational Problem | Candidate Algorithms & Complexity | Selected Primary vs. Baseline | Data Invariant & Justification |
| :---: | :--- | :--- | :--- | :--- |
| **A** | **Relief Inventory**<br>*(0/1 Knapsack)* | 1. 1D Tabular DP: $O(nW)$<br>2. Branch & Bound: $O(2^n)$<br>3. Greedy Ratio: $O(n \log n)$ | **Primary:** 1D DP $O(nW)$<br>**Baseline:** Greedy ratio $O(n \log n)$ | Integer crate weights ($w_i \le 20$, $W \le 30,000$). Pseudo-polynomial DP runs in milliseconds. Fails if weights are continuous reals. |
| **B** | **Route Planning**<br>*(Single-Source Shortest Path)* | 1. Dijkstra (Min-Heap): $O((V+E)\log V)$<br>2. Bellman-Ford: $O(VE)$<br>3. Unweighted BFS: $O(V+E)$ | **Primary:** Dijkstra $O((V+E)\log V)$<br>**Baseline:** Bellman-Ford $O(VE)$ | Road traversal minutes $\ge 1$ and location penalties $\ge 0$. Non-negative edge invariant holds strictly. Fails if negative cycles exist. |
| **C** | **Rescue Scheduling**<br>*(Weighted Interval Scheduling)* | 1. Greedy EFT: $O(m \log m)$<br>2. DP + Binary Search: $O(m \log m)$<br>3. Integer LP: $O(2^m)$ | **Primary:** DP + Bisect $O(m \log m)$<br>**Baseline:** Brute-force $O(2^m)$ | 1D time domain $[0, 1440]$. Sorted finish times guarantee optimal substructure via predecessor lookup. Fails with multi-crew dependencies. |
| **D** | **Emergency Queue**<br>*(Priority Queue Simulation)* | 1. Dial's Bucket Queue: $O(A + K)$<br>2. Binary Max-Heap: $O(A \log A)$<br>3. Unsorted Scan: $O(A^2)$ | **Primary:** Dial's Buckets $O(A)$<br>**Baseline:** Binary Heap $O(A \log A)$ | Urgency priorities are discrete integers bounded in $[1, 10]$ ($K=10$). Array buckets yield $O(1)$ amortized operations. |
| **E** | **Radio Logs**<br>*(Exact Pattern Search & Coding)* | 1. KMP Search: $O(N + M)$<br>2. Wagner-Fischer: $O(L_a L_b)$<br>3. Huffman Tree: $O(\|\Sigma\| \log \|\Sigma\|)$ | **Primary:** KMP + Huffman<br>**Baseline:** Naive Match $O(NM)$ | Discrete alphabet ($\|\Sigma\|=38$) and static log text. KMP deterministic failure function prevents catastrophic backtracking. |
| **F** | **Network Planning**<br>*(Minimum Spanning Tree)* | 1. Kruskal + DSU: $O(E \alpha(V))$<br>2. Prim (Binary Heap): $O(E \log V)$<br>3. Borůvka: $O(E \log V)$ | **Primary:** Kruskal + DSU $O(E \alpha(V))$<br>**Baseline:** Prim's $O(E \log V)$ | Graphs are sparse ($E \le 3V$) with integer cable costs $[1, 100]$. Counting sort reduces Kruskal sorting step to $O(E)$. |
| **G** | **Chains and Cuts**<br>*(Matrix Chain & Rod Cutting)* | 1. Tabular DP: $O(n^3)$ MCM, $O(L^2)$ Cut<br>2. Memoized Recursion: $O(n^3)$<br>3. Greedy Dimension Heuristic | **Primary:** Tabular DP $O(n^3) / O(L^2)$<br>**Baseline:** Greedy heuristic | Strict optimal substructure and acyclic subproblem dependencies. Stage counts ($n \le 300$) and drum lengths ($L \le 2000$) execute rapidly. |
| **H** | **Hard Planning Questions**<br>*(3-SAT, Subset Sum, TSP, MVC)* | 1. CDCL/DPLL for 3-SAT<br>2. Meet-in-the-Middle: $O(2^{n/2})$<br>3. Held-Karp: $O(n^2 2^n)$ / 2-Opt<br>4. FPT Vertex Cover: $O(1.2738^k + kn)$ | **Primary:** Exact solvers & FPT<br>**Baseline:** Brute-force $O(2^n)$ / $O(n!)$ | Planted solutions exist by construction. Small Tier S parameters ($n \le 15$) allow provable global verification. |
| **I** | **Nearest Sites & Checksums**<br>*(Closest Pair & Long Integer Prod)* | 1. D&C Closest Pair: $O(n \log n)$<br>2. Karatsuba Multiplication: $O(d^{1.585})$<br>3. Naive Scan: $O(n^2) / O(d^2)$ | **Primary:** D&C Pair + Karatsuba<br>**Baseline:** Pairwise $O(n^2) / O(d^2)$ | 2D coordinates in $[0, 999]^2$ permit geometric strip pruning (at most 7 candidates). High-precision crate serial products reach $10^4$ digits. |

---

## 🔍 Independent Validation Suite & Test Results

The engine executes an independent 8-layer validator ([`validator/validate.py`](validator/validate.py)):

* **V1 (Structure)**: 20 required sheets in exact canonical order, matching headers, non-empty content.
* **V2 (Types & Ranges)**: Case IDs, integer bounds, coordinates in $[0, 999]^2$, valid categories $[0, 4]$, penalties $\{0, 1, 2, 4, 6\}$.
* **V3 (Referential Integrity)**: Foreign keys across sheets, consecutive indexing, targets exist as shelters/hospitals (`S` or `H`).
* **V4 (Network Connectivity & Closures)**: Initial road graph is connected; closure wave partitions do not overlap.
* **V5 (Exact Claim Verification)**: Re-solves Tier S claims independently (0/1 knapsack, interval scheduling, rod cut, TSP, MVC) and asserts exact arithmetic equality.
* **V6 (Planted Witnesses)**: Verifies planted 3-SAT satisfying assignment, exact subset sum target, planted tour validity, and sensor vertex cover.
* **V7 (Signature Rules)**: Validates case-study specific constraints (degree bounds, closure wave counts, cargo spoilage ratios, beacon distributions).
* **V8 (Trap Rules)**: Validates adversarial properties on Tier X (Cases 46–49).

### 📊 Validation Results Summary

```text
================================================================================
LIFELINE ALGORITHMIC RELIEF-COMMAND ENGINE: VALIDATION AUDIT REPORT
================================================================================
Target Workbook: cases.xlsx
Total Cases Evaluated: 50 (IDs: 39-00 through 39-49)
Verdict: ALL 50 CASES PASSED (0 ERRORS, 0 WARNINGS)

Cross-Case Variety Distribution Checks:
  ✔ Knapsack greedy suboptimal in Tier S: 12 cases (Requirement: >= 5)  -> PASS
  ✔ Min-hop route costs more in Tier S:   12 cases (Requirement: >= 5)  -> PASS
  ✔ 3-SAT Clause/Variable Hardness Ratios across 26 M/L instances:
      - Under-constrained (< 3.5):          7 cases (Requirement: >= 5)  -> PASS
      - Phase Transition Window (3.5-4.8): 11 cases (Requirement: >= 8)  -> PASS
      - Over-constrained (> 4.8):           8 cases (Requirement: >= 5)  -> PASS
  ✔ Cross-case uniqueness of module selections:                          -> PASS

Adversarial Corrupted Copies (validator/tests/):
  ✔ TEST 1:  caseA_broken_V1_missing_sheet.xlsx           -> REJECTED (Missing 'claims' sheet)
  ✔ TEST 2:  caseA_broken_V2_crate_weight.xlsx            -> REJECTED (Crate weight 99 kg > 20)
  ✔ TEST 3:  caseA_broken_V3_invalid_target.xlsx          -> REJECTED (Non-existent target node 9999)
  ✔ TEST 4:  caseA_broken_V4_disconnected_network.xlsx    -> REJECTED (Disconnected road graph)
  ✔ TEST 5:  caseA_broken_V5_corrupted_claim.xlsx         -> REJECTED (Corrupted claim cargo_opt)
  ✔ TEST 6:  caseB_broken_V2_invalid_penalty.xlsx         -> REJECTED (Invalid penalty value 5)
  ✔ TEST 7:  caseB_broken_V3_nonconsecutive_crate_id.xlsx -> REJECTED (Discontinuous crate_id)
  ✔ TEST 8:  caseB_broken_V4_overlapping_waves.xlsx       -> REJECTED (Duplicate road across waves)
  ✔ TEST 9:  caseB_broken_V6_invalid_vertex_cover.xlsx    -> REJECTED (Invalid sensor cover set)
  ✔ TEST 10: caseB_broken_V7_signature_priority.xlsx      -> REJECTED (Violates mean alarm urgency)
================================================================================
OVERALL VALIDATION AUDIT VERDICT: 100% PASS
================================================================================
```

---

## 🚀 Setup & Reproduction Guide

### Prerequisites
* Python 3.10 or higher
* Required dependencies:
  ```bash
  pip install openpyxl reportlab pypdf
  ```

### Complete End-to-End Execution

```bash
# Clone the repository
git clone https://github.com/faizanzahid-ai/22I-0533-B_22I-0074-B_22I-0547-B.git
cd 22I-0533-B_22I-0074-B_22I-0547-B

# 1. Generate master dataset (50 cases from Group Seed 39)
python generator/generate.py --seed 39 --output cases.xlsx

# 2. Generate the 10 adversarial broken test workbooks
python validator/generate_tests.py

# 3. Execute the full validation suite and produce validation_report.txt
python validator/run_validation.py

# 4. Compile the 2-page Algorithm Selection Proposal PDF
python proposal_generator.py

# 5. Compile the 2-page Approach Brief PDF
python -c "from approach_generator import generate_approach_pdf; generate_approach_pdf()"
```

---

## 📜 Academic Integrity & Compliance

This software, benchmark data, and documentation have been developed in strict accordance with the academic integrity guidelines of the National University of Computer and Emerging Sciences (FAST-NUCES).

* **Deterministic Provenance**: All 50 cases in `cases.xlsx` are generated programmatically from group seed `39` with **zero manual alteration**.
* **Zero Plagiarism**: All algorithmic selection justifications, model parameters, and code implementations are the original work of Group 39.
* **Audit Trail**: Full commit history reflects continuous, incremental engineering across all components.

---
*Maintained by Group 39 (Ch Faizan Zahid, Mohid Abbas, Fizan Tariq) — Department of AI, FAST-NUCES Islamabad.*

---

## 📜 Academic Integrity & Compliance

This software, benchmark data, and documentation have been developed in strict accordance with the academic integrity guidelines of the National University of Computer and Emerging Sciences (FAST-NUCES).

* **Deterministic Provenance**: All 50 cases in `cases.xlsx` are generated programmatically from group seed `39` with **zero manual alteration**.
* **Zero Plagiarism**: All algorithmic selection justifications, model parameters, and code implementations are the original work of Group 39.
* **Audit Trail**: Full commit history reflects continuous, incremental engineering across all components.

---
*Maintained by Group 39 (Ch Faizan Zahid, Mohid Abbas, Fizan Tariq) — Department of Computer Science & AI, FAST-NUCES Islamabad.*
