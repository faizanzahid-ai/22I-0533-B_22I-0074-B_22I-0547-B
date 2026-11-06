"""Constants of the LIFELINE world: tiers, ranges, alphabet and the size sub-ranges we draw from.

All legal ranges are copied from Section 3 of the project statement.  DRAW holds the
(narrower) ranges our generator actually samples from; every DRAW range lies inside the
legal range of its tier.
"""
import random

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"   # 38 symbols
PATTERN_LENGTHS = [2, 4, 8, 12, 20, 40]
MAX_CELL = 10_000                                     # symbols per radio_log cell
PENALTIES = [0, 1, 2, 4, 6]

# Legal ranges of Section 3 (inclusive).
LEGAL = {
    "S": dict(crates=(8, 20), V=(6, 12), waves=(2, 5), log=(200, 500), report=(10, 30),
              windows=(8, 20), alarms=(10, 40), sites=(5, 9), stages=(4, 8), drum=(5, 14),
              sensors=(6, 14), safety=(6, 15), rations=(8, 20)),
    "M": dict(crates=(40, 200), V=(30, 150), waves=(2, 5), log=(2000, 10000), report=(30, 150),
              windows=(50, 300), alarms=(200, 1000), sites=(10, 16), stages=(15, 60), drum=(40, 200),
              sensors=(20, 40), safety=(20, 50), rations=(24, 40)),
    "L": dict(crates=(500, 1500), V=(500, 2000), waves=(2, 5), log=(20000, 100000), report=(200, 1000),
              windows=(1000, 3000), alarms=(2000, 5000), sites=(200, 500), stages=(100, 300),
              drum=(500, 2000), sensors=(100, 400), safety=(20, 50), rations=(50, 100)),
}
LEGAL["X"] = dict(LEGAL["L"])

# Trap cases override some tier-X ranges (Section 2).
TRAP_OVERRIDES = {
    46: {"crates": (1500, 3000)},
    47: {"crates": (12, 60)},
    48: {"V": (1500, 3000)},
    49: {"log": (50000, 100000)},
}

# What we actually draw.  Tier L / X use the lower part of each legal range so the
# workbook stays a few MB and Iteration-2 experiments remain quick; every value is legal.
DRAW = {
    "S": dict(LEGAL["S"]),
    "M": dict(LEGAL["M"]),
    "L": dict(crates=(500, 900), V=(500, 900), waves=(2, 5), log=(20000, 40000), report=(200, 400),
              windows=(1000, 1600), alarms=(2000, 3000), sites=(200, 300), stages=(100, 200),
              drum=(500, 900), sensors=(100, 200), safety=(20, 50), rations=(50, 100)),
}
DRAW["X"] = dict(DRAW["L"])
TRAP_DRAW = {
    46: {"crates": (1500, 1800)},
    47: {"crates": (12, 16)},
    48: {"V": (1500, 1700)},
    49: {"log": (50000, 60000)},
}

SCENARIO_NAMES = {
    1: "Delta Flood", 2: "Mountain Earthquake", 3: "Coastal Cyclone",
    4: "Urban Flash Flood", 5: "Landslide Corridor", 6: "Outbreak Camp",
}


def tier_of(k):
    if k < 20:
        return "S"
    if k < 40:
        return "M"
    if k < 46:
        return "L"
    return "X"


def scenario_of(k):
    return k % 6 + 1


def draw_range(k, item):
    """Range the generator samples `item` from for case k."""
    if k in TRAP_DRAW and item in TRAP_DRAW[k]:
        return TRAP_DRAW[k][item]
    return DRAW[tier_of(k)][item]


def rng_for(seed, k, module, attempt=0):
    """Every random stream depends only on the group seed, the case number and the module
    name (plus a retry counter).  String seeds are hashed with SHA-512 by `random`, so the
    stream is identical on every machine and Python version >= 3.2."""
    return random.Random(f"LIFELINE|{seed}|{k}|{module}|{attempt}")
