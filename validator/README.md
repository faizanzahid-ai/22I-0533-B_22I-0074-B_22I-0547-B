# LIFELINE validator

```
python validator/validate.py cases.xlsx                       # prints PASS or the broken rules per case
python validator/make_tests.py cases.xlsx                     # rebuilds validator/tests/
python validator/run_report.py cases.xlsx validation_report.txt
```

The validator does not import the generator and trusts no field. Every count, bound, claim and
planted object is recomputed in `algos.py`:

- pattern counts: KMP
- edit distance: DP
- shortest routes: Dijkstra
- fewest-roads routes: DP over BFS layers
- cargo: knapsack DP
- windows: earliest-finish greedy and weighted-interval DP
- drum: rod-cutting DP
- tour: Held-Karp
- sensors: branch-and-bound vertex cover
- tier L/X tours: nearest-neighbour check

Check tags follow Section 4:

| tag | what is checked |
|---|---|
| V1 | sheets, headers, cell types, sort order, case_id format, tier, scenario |
| V2 | sizes and value ranges per tier |
| V3 | ids and references |
| V4 | connectivity and waves |
| V5 | pattern counts, edit_bound, log parts, tier-S claims |
| V6 | planted tour, cover, assignment and rations |
| V7 | signature rules and the four variety rules |
| V8 | the four traps |

`tests/` holds 3 valid single-case workbooks (cases 00, 01 and 47) and 19 broken copies. Cases 00
and 01 are each broken in 9 different ways; each copy has one defect, listed in `tests/README.md`.
Test files are checked with `--subset`, which skips the whole-workbook rules (50 cases, variety).
