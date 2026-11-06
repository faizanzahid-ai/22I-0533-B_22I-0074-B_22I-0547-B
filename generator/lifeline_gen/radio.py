"""Radio data (module E): the log, the six search patterns and the two reports."""
from collections import Counter

from .config import ALPHABET, PATTERN_LENGTHS, MAX_CELL

WORDS = {
    1: ["FLOOD", "WATER", "FOOD", "LEVEE", "BOAT", "ROAD", "UNDER", "VILLAGE", "SOS"],
    2: ["QUAKE", "MEDIC", "TOOLS", "RUBBLE", "AFTERSHOCK", "INJURED", "TRAPPED", "SOS"],
    3: ["SURGE", "PORT", "SHELTER", "WIND", "EVAC", "BOATS", "STATIC", "SOS"],
    4: ["STREET", "PUMP", "SUBWAY", "RESCUE", "RARE-KIT", "BLOCK", "SOS"],
    5: ["SLIDE", "KM", "HWY-1", "CUTOFF", "CONVOY", "GORGE", "SOS"],
    6: ["BEACON", "ORS", "WATER", "MED", "CAMP-3", "SPOILED", "FEVER"],
}
NOISE_P = {1: 0.12, 2: 0.12, 3: 0.45, 4: 0.15, 5: 0.10, 6: 0.05}


def gen_log(rng, N, scenario):
    words = WORDS[scenario]
    parts = []
    size = 0
    beacon = "BEACON_" + str(rng.randint(1, 9)) + "_" + rng.choice(words[1:])
    while size < N:
        r = rng.random()
        if r < NOISE_P[scenario]:
            s = "".join(rng.choices(ALPHABET, k=rng.randint(1, 8)))
        elif scenario == 6 and r < 0.55:
            s = beacon + "____"                                # repeated beacon message
        else:
            s = rng.choice(words) + "_" + str(rng.randint(0, 999)) + rng.choice("_-")
        parts.append(s)
        size += len(s)
    log = list("".join(parts)[:N])
    if scenario == 6:                       # one symbol (the separator) >= 25% of the log
        top = "_"
        idx = [i for i, ch in enumerate(log) if ch != top]
        rng.shuffle(idx)
        cnt = log.count(top)
        while cnt * 4 < N + 8:
            log[idx.pop()] = top
            cnt += 1
    if scenario == 3:                       # the noisy log uses >= 30 of the 38 symbols
        missing = [ch for ch in ALPHABET if ch not in set(log)]
        for ch in missing:
            log[rng.randrange(N)] = ch
    return "".join(log)


def count_occurrences(text, pat):
    """Occurrences of pat in text, overlaps included."""
    c, i = 0, text.find(pat)
    while i >= 0:
        c += 1
        i = text.find(pat, i + 1)
    return c


def gen_patterns(rng, log):
    """Patterns 0..2 are cut from the log (they occur); 3 and 4 are cut or random;
    5 (length 40) is random and must not occur."""
    pats = []
    for i, L in enumerate(PATTERN_LENGTHS):
        if i <= 2 or (i <= 4 and rng.random() < 0.5):
            p = rng.randrange(len(log) - L + 1)
            pats.append(log[p:p + L])
        else:
            while True:
                s = "".join(rng.choices(ALPHABET, k=L))
                if count_occurrences(log, s) == 0:
                    pats.append(s)
                    break
    return [(p, count_occurrences(log, p)) for p in pats]


def split_log(log):
    return [log[i:i + MAX_CELL] for i in range(0, len(log), MAX_CELL)]


def gen_reports(rng, lo, hi, scenario):
    """report_a is a radio report; report_b is report_a after `ops` random edits.
    edit_bound = ops is an upper bound on the true edit distance by construction."""
    la = rng.randint(lo, hi)
    words = WORDS[scenario]
    s = ""
    while len(s) < la:
        s += rng.choice(words) + "_" + str(rng.randint(0, 99)) + "-"
    a = list(s[:la])
    b = list(a)
    ops = rng.randint(1, max(1, la // 4))
    done = 0
    for _ in range(ops):
        kind = rng.choice("IDR")
        if kind == "I" and len(b) < hi:
            b.insert(rng.randint(0, len(b)), rng.choice(ALPHABET))
        elif kind == "D" and len(b) > lo:
            del b[rng.randrange(len(b))]
        else:
            i = rng.randrange(len(b))
            b[i] = rng.choice([c for c in ALPHABET if c != b[i]])
        done += 1
    return "".join(a), "".join(b), done


def symbol_stats(log):
    c = Counter(log)
    return len(c), c.most_common(1)[0][1]
