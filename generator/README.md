# LIFELINE generator

Writes `cases.xlsx` (50 cases, 20 sheets) from the group seed. Run this one command from the project root:

```
python generator/generate.py --seed 39 --out cases.xlsx
```

It needs Python 3.8 or newer and `openpyxl` (`pip install openpyxl`), and takes about 30 seconds.
All randomness comes from `random.Random("LIFELINE|<seed>|<case>|<module>|<attempt>")`, so the same
command always writes the same data.

| file | contents |
|---|---|
| `lifeline_gen/config.py` | tiers, legal ranges, the sub-ranges we draw from, seeded RNG |
| `lifeline_gen/inventory.py` | crates, capacity, greedy and DP knapsack checks |
| `lifeline_gen/network.py` | locations, roads (geographic and corridor builders), waves, bridges, route checks |
| `lifeline_gen/radio.py` | radio log, the six patterns and their counts, the two reports and edit_bound |
| `lifeline_gen/schedule.py` | rescue windows (touching pairs, overlap) and alarms |
| `lifeline_gen/planted.py` | sites and the planted tour, pipeline, drum, sensor cover, safety assignment, rations |
| `lifeline_gen/claims.py` | exhaustive-search optima for the tier-S claims |
| `lifeline_gen/traps.py` | trap cases 46-49 |
| `lifeline_gen/workbook.py` | sheet and column layout; writes the xlsx |

Library use: `openpyxl` only writes the file, and `random` only draws numbers. Every check and optimum
is computed by our own code.
