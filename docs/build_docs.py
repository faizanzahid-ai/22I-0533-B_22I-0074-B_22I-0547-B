"""Build approach_note.pdf, proposal.pdf, members.txt and repository.txt from members.json.

    python docs/build_docs.py
"""
import json
import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Table, TableStyle, PageBreak, Spacer)

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
CFG = json.load(open(os.path.join(ROOT, "members.json")))
MEM = CFG["members"]
NAME = "_".join(f"{m['roll']}-{m['section']}" for m in MEM)

body = ParagraphStyle("b", fontName="Helvetica", fontSize=9.6, leading=12.3, spaceAfter=3.2, alignment=4)
h1 = ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=12, leading=14, spaceAfter=3)
h2 = ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=11, leading=13.5, spaceBefore=5, spaceAfter=2.5)
cell = ParagraphStyle("c", fontName="Helvetica", fontSize=6.9, leading=8.1)
cellb = ParagraphStyle("cb", parent=cell, fontName="Helvetica-Bold")


def P(t, s=body):
    return Paragraph(t, s)


# ============================================================================ approach note
APPROACH = [
    ("h1", f"LIFELINE - Approach note (Iteration 1, group {CFG['group']}, seed {CFG['group']})"),
    ("p", "All 50 cases come from <b>generator/generate.py</b>. Every random stream is "
          "<i>Random(\"LIFELINE|seed|case|module|attempt\")</i>, so a case depends only on the group seed and "
          "its case number, and the modules are independent of each other. When a case has to meet a rule "
          "that cannot be built in directly (for example 'greedy is not optimal'), the generator checks it and "
          "redraws with attempt + 1, so the result is still deterministic. Tier L/X sizes come from the lower "
          "part of each legal range (for example V 500-900, crates 500-900, log 20k-40k). This keeps the workbook at "
          "2.8 MB and keeps Iteration-2 baselines (O(n<super>2</super>), O(nW)) runnable."),
    ("h2", "1. From story to numbers"),
    ("p", "<b>Common model.</b> Locations are random points in a unit square. Each joins a random one of its 3 "
          "nearest earlier points (a geographic spanning tree), then extra roads go to one of the 3-14 nearest "
          "neighbours until E is reached. Minutes grow with road length; 30% of roads are 'damaged' and take "
          "1.8-3.5x longer. Cable cost follows length. Crates follow category profiles: food and water are heavy "
          "and cheap (6-20 kg, 10-65), medicine is light and valuable (1-8 kg, 40-100), rare kit is 60-100. "
          "Capacity is 25-55% of the total weight."),
    ("p", "<b>1 Delta Flood</b> - <i>'a flat delta of small villages joined by raised roads'</i>: E = 1.15-1.5V "
          "(average degree 2.3-3.0), few alternatives. <i>'Roads go under water in waves'</i>: 3-5 waves. Penalty "
          "weights favour 2/4/6, so at least 40% of locations are wet (78-92% in the tier-S flood cases). <i>'Food and water matter most'</i>: "
          "category weights 34/30% and a hard minimum of 58%. "
          "||<b>2 Mountain Earthquake</b> - <i>'a few roads and almost no alternatives'</i>: E = 1.03-1.25V (degree 2.17-2.57). "
          "<i>'The injured need medicine and tools'</i>: at least 48% cat 2/3. <i>'Bursts of urgent calls follow each "
          "aftershock'</i>: 65% of alarms land in exponential bursts after 3-6 shock ticks, and priorities are "
          "skewed to 7-10 (mean 6.2-7.5). "
          "||<b>3 Coastal Cyclone</b> - <i>'a port city and fishing villages'</i>: 42% shelter weight, forced to at least 25%. "
          "<i>'Rescue windows are short and overlap'</i>: 20-120 min windows packed round 1-4 surge times, so each "
          "overlaps 2 or more others on average. <i>'The radio is full of noise'</i>: 45% of the log is uniform noise, "
          "and every case uses 34 or more symbols. "
          "||<b>4 Urban Flash Flood</b> - <i>'a dense city with many alternative routes'</i>: E = 1.8-2.5V (degree 3.6-4.9). "
          "<i>'Calls arrive faster than anyone can answer'</i>: 1.55-1.75 alarms per tick. <i>'Rare equipment is "
          "available'</i>: at least 12% cat 4. "
          "||<b>5 Landslide Corridor</b> - <i>'a single mountain highway along a gorge'</i>: a path of 0.45-0.6V roads "
          "from the HQ, with villages hanging off it and degree at most 4. That makes the farthest location 0.45V "
          "or more roads away (at least floor(V/4)). <i>'A collapse cuts off whole communities'</i>: wave 1 always contains "
          "a bridge whose far side holds a target. "
          "||<b>6 Outbreak Camp</b> - <i>'Medicine and water count and supplies spoil'</i>: at least 58% cat 1/2, and 65% of "
          "expiries are 0-300. <i>'Radio beacons repeat the same messages'</i>: half of the log is one repeated beacon "
          "with '_' separators, and '_' is topped up to at least 25% of the log."),
    ("p", "Other choices: windows are 60% short (5-120 min) and 40% long (121-480 min), with value rising with "
          "duration. Sites sit in 2-5 village clusters (strung along the valley for study 5). Drum price is about "
          "A*j<super>g</super> (g = 0.7-1.05) with noise and a 12% premium on one standard length. Safety rules are "
          "random 3-literal rules. Ration values sit near a base of 40-400."),
    ("h2", "2. Planted objects and claims"),
    ("p", "<b>Tour</b>: first the nearest-neighbour tour from site 0 (ties go to the smaller id), then strictly "
          "improving 2-opt moves. So the tour is a permutation that starts at 0, and it is never longer than the "
          "nearest-neighbour tour, which the L/X rule requires. tour_length is its closed Manhattan length. "
          "<b>Cover</b>: the k cover nodes are chosen first (2 &lt;= k &lt;= n/2). Every other node gets an edge to "
          "a cover node, and the extra edges up to n-1+k or more always have a cover endpoint, so the cover touches every "
          "edge by construction. <b>Assignment</b>: the switch values are drawn first. Each rule takes 3 different "
          "switches with random signs; if no literal is true, one sign is flipped. rules/switches is set by "
          "the band of each case (variety rule 3: 7 low, 11 mid, 8 high). <b>Rations</b>: a random subset of n/4-n/2 "
          "items is chosen and rations_target is its sum. <b>edit_bound</b>: report_b is report_a after 'ops' random "
          "insert/delete/replace steps, and edit_bound = ops. That is always at least the true distance and at most "
          "len_a + len_b. <b>Pattern counts</b>: patterns 0-2 are cut from the log, so they occur. Pattern 5 (length "
          "40) is random and redrawn until it does not occur. Counts include overlaps. <b>Claims (tier S)</b> are "
          "found by exhaustive search in generator/lifeline_gen/claims.py: all subsets of crates, all compatible "
          "window chains, all partitions of the drum, all tour orders and all node subsets. The validator recomputes "
          "them with different methods (knapsack DP, earliest-finish greedy, weighted-interval DP, rod-cutting DP, "
          "Held-Karp and branch-and-bound vertex cover), so two independent methods agree."),
    ("h2", "3. The traps"),
    ("p", "<b>46 Dock-order</b> (1,765 crates): weights sorted ascending, values sorted descending and serials "
          "ascending. Four of the five fields (weight, value, serial and value-per-kg) are monotone. A quicksort with "
          "first or last pivot hits its O(n<super>2</super>) case, and a ratio-sort finds work already done (or "
          "reversed). Checked by V8 (monotone fields, exact cross-multiplication) and V2 (1,500-3,000 crates). "
          "||<b>47 Best-looking crate</b> (16 crates, capacity 20): one 1 kg 'bait' with the best value/kg, one or two "
          "20 kg crates worth 90-100, and 10-13 kg fillers worth 10-15. Greedy by value/kg takes the bait and then "
          "cannot fit any 20 kg crate. It reaches 48% of the optimum (60% allowed). V8 recomputes greedy and the "
          "knapsack DP. "
          "||<b>48 Shortest-looks-cheapest</b> (1,691 locations): a highway of 520-600 roads where villages only connect "
          "neighbouring highway positions, so two locations are 520 or more roads apart (567 in case 48). Next to the HQ, HQ-a-T is "
          "2 roads of 55-60 min through a penalty-6 junction, and HQ-b1-b2-T is 3 roads of 1-3 min. BFS returns a "
          "route costing 118 against a cheapest of 8. V8 runs a double-sweep BFS (a lower bound on the diameter), Dijkstra "
          "and a DP over BFS layers. "
          "||<b>49 Near-miss</b> (58,972 symbols): 92-95% of the log is one symbol repeated (a stuck carrier), then a "
          "noise tail without that symbol. Every pattern is (len-1) copies of the symbol plus one other symbol, so "
          "its prefix matches at about 93% of start positions while the pattern occurs at most once. Naive search "
          "costs about n*m. V8 checks the periodic run (at least 90%) and the prefix-match share for 4 or more patterns."),
    ("h2", "4. What will be hard"),
    ("p", "<b>Delta Flood</b>: (B) re-routing after each wave, because 40% or more of locations carry penalties, "
          "so the cheapest route is often not the fewest-roads one; (A) loading heavy, cheap food and water under "
          "a tight capacity, where greedy is suboptimal in 13 of 20 tier-S cases. ||<b>Earthquake</b>: (B) with degree "
          "about 2.2 one closure can leave no route at all, so the 'no route' output matters; (D) bursty, "
          "high-priority alarms, where many ties at priority 8-10 make tie-breaking and heap order visible. "
          "||<b>Cyclone</b>: (C) packed, short, overlapping windows where max-count and max-value schedules differ; "
          "(E) the Huffman code on a nearly uniform 38-symbol noise log, where the saving over 6-bit fixed codes is small. "
          "||<b>Urban</b>: (D) 1.55-1.75 alarms per tick means the queue grows without bound and most alarms wait "
          "long; (F) average degree 3.6-4.9, so the MST must choose among many near-equal cables. "
          "||<b>Landslide</b>: (B) targets cut off by bridge closures (the answer is 'no route'); (F) the "
          "network is a near-tree, so after waves the MST must span only the reachable part. ||<b>Outbreak</b>: (A) "
          "valuable medicine that expires early (values of the day); (E) a log where one symbol is 25% or more, which "
          "makes Huffman codes very unbalanced and makes naive search slow on repeated beacon prefixes."),
]


def build_approach(path):
    doc = SimpleDocTemplate(path, pagesize=A4, leftMargin=14 * mm, rightMargin=14 * mm,
                            topMargin=11 * mm, bottomMargin=11 * mm,
                            title="LIFELINE approach note", author=f"Group {CFG['group']}")
    flow = []
    for kind, text in APPROACH:
        for part in text.split("||"):
            flow.append(P(part.strip(), h1 if kind == "h1" else h2 if kind == "h2" else body))
    doc.build(flow)


# ============================================================================ proposal
MODULES = [
    ("A. Relief inventory",
     "n crates (w<sub>i</sub> in 1..20, v<sub>i</sub>), capacity W. Choose a subset with total weight &lt;= W that "
     "maximises total value (0/1 knapsack, NP-hard in general).",
     "DP over capacity O(nW) time, O(W) space; branch and bound with fractional bound O(2<super>n</super>) worst; "
     "exhaustive O(2<super>n</super>); greedy by value/kg O(n log n) (not exact).",
     "<b>Primary:</b> DP O(nW) with a back-pointer table to recover the set. <b>Baseline:</b> greedy by value/kg "
     "and exhaustive on tier S.",
     "Weights are small integers, so W &lt;= 0.7*20n; the largest case is n=1765, W=9541 (about 17M cells). It would fail "
     "for real-valued or huge weights (W far above n), where B&amp;B or meet-in-the-middle is needed. Trap 47 shows greedy reaching 48%."),
    ("B. Route planning",
     "Graph V, E with non-negative step cost minutes + penalty(v) &gt;= 1; source HQ; today's closed roads. Output "
     "the cheapest route and its cost or 'no route', the reachable set and a fewest-roads route.",
     "Dijkstra with binary heap O((V+E) log V); Dijkstra with array O(V<super>2</super>); Bellman-Ford O(VE); "
     "BFS O(V+E) for reachability and fewest roads.",
     "<b>Primary:</b> Dijkstra (binary heap) plus BFS. <b>Baseline:</b> Bellman-Ford (and BFS route cost for "
     "comparison).",
     "All costs are positive and the graphs are sparse (E &lt;= 3V), so the heap beats O(V<super>2</super>). "
     "It would fail with negative costs (not possible here). Trap 48: the BFS route costs 118 against a cheapest of 8 (about 15x)."),
    ("C. Rescue scheduling",
     "n windows [s<sub>i</sub>, f<sub>i</sub>) with value v<sub>i</sub>. Pick pairwise compatible windows "
     "(f<sub>i</sub> &lt;= s<sub>j</sub> allowed): (1) most windows, (2) most total value.",
     "(1) earliest-finish greedy O(n log n); (2) weighted interval DP + binary search O(n log n); "
     "exhaustive O(2<super>n</super>); greedy by value (not exact).",
     "<b>Primary:</b> earliest-finish greedy and weighted-interval DP. <b>Baseline:</b> exhaustive search "
     "(tier S claims) and greedy by value.",
     "Rests on the exchange argument: touching windows count as compatible, so compare with &lt;=. Cyclone "
     "windows overlap heavily, so count and value schedules differ. It would fail if windows needed travel "
     "time between them (that becomes a routing problem)."),
    ("D. Emergency queue",
     "n alarms (tick, priority 1..10). Each tick, first add the arrivals, then release the most urgent alarm "
     "present (ties: earlier alarm_id). Output the release order.",
     "Binary max-heap O(n log n); unsorted list with linear scan O(n<super>2</super>); sorted insertion O(n<super>2</super>); "
     "10 FIFO buckets O(n + T*10).",
     "<b>Primary:</b> our own binary heap keyed (-priority, alarm_id). <b>Baseline:</b> linear-scan list.",
     "Arrival rate is 1.2-1.8 per tick against 1 release, so the backlog grows to about 0.5n, where the gap between "
     "O(log n) and O(n) shows. Buckets would win if priorities stay in 1..10, but they do not generalise."),
    ("E. Radio logs",
     "Log of n symbols (38-symbol alphabet), pattern of length m; reports of length a and b. Find all start "
     "positions (overlaps included), the edit distance with a script, and a minimum prefix-free code.",
     "Search: naive O(nm), KMP O(n+m), Rabin-Karp O(n+m) expected; edit distance: DP O(ab), Hirschberg O(ab) "
     "time and O(a+b) space; code: Huffman O(s log s) with s = 38, fixed 6-bit code.",
     "<b>Primary:</b> KMP, Wagner-Fischer DP with traceback, Huffman with our own heap. <b>Baseline:</b> naive "
     "search, fixed-length 6-bit code.",
     "Trap 49 (93% one symbol) drives naive search to about n*m, while KMP stays linear. Reports are at most 1000, so "
     "a full DP table (1M cells) fits. Huffman gains little on the near-uniform Cyclone noise."),
    ("F. Network planning",
     "Undirected graph on the locations reachable from the HQ, cable cost c<sub>e</sub> 1..100. Find roads "
     "linking all of them with minimum total cable (MST).",
     "Kruskal with union-find O(E log E); Prim with binary heap O(E log V); Prim with array O(V<super>2</super>).",
     "<b>Primary:</b> Kruskal + union-find (path compression, union by rank). <b>Baseline:</b> Prim (heap).",
     "Sparse graphs (E &lt;= 3V) and integer costs with many ties. Kruskal on the reachable part gives a spanning "
     "tree; on a disconnected graph it gives a forest, so we restrict to HQ's component first. Prim "
     "(array) is better only for dense graphs."),
    ("G. Chains and cuts",
     "n+1 dims d<sub>0..n</sub>: bracketing with the fewest scalar multiplications. Drum length L with price p<sub>j</sub>: "
     "cuts with maximum total price.",
     "Matrix chain: DP O(n<super>3</super>) / O(n<super>2</super>) space, exhaustive Catalan(n); rod cutting: "
     "DP O(L<super>2</super>), exhaustive 2<super>L-1</super>, greedy by price per length.",
     "<b>Primary:</b> both DPs with split/cut reconstruction. <b>Baseline:</b> left-to-right product and greedy "
     "density cut; exhaustive on tier S.",
     "n &lt;= 300 gives 4.5M DP steps and L &lt;= 2000 gives 2M, both fine. Prices are deliberately not proportional "
     "and carry premium lengths, so greedy density fails. O(n<super>3</super>) would be too slow only for n in the thousands."),
    ("H. Hard planning questions",
     "3-SAT on v switches, m rules; subset sum of n values to target T; TSP on n sites (Manhattan); vertex cover "
     "of size &lt;= k on a graph with n nodes and m edges.",
     "SAT: brute force O(2<super>v</super>m), DPLL with unit propagation O(2<super>v</super>) worst; subset sum: "
     "DP O(nT), meet-in-the-middle O(2<super>n/2</super>); TSP: Held-Karp O(n<super>2</super>2<super>n</super>), "
     "NN + 2-opt O(n<super>2</super>) per pass; cover: bounded search tree O(2<super>k</super>(n+m)), "
     "brute force C(n,k).",
     "<b>Primary:</b> DPLL; subset-sum DP with bitset; Held-Karp (n &lt;= 16), NN + 2-opt (n &gt; 16); FPT "
     "branching on an uncovered edge. <b>Baseline:</b> brute force on tier S plus the planted answers.",
     "v &lt;= 50 and rules/var spread over 2.6-5.8 (around the 4.26 hardness peak); T &lt;= 1e5, so DP fits; "
     "TSP is exact only up to 16 sites; k &lt;= 53 makes 2<super>k</super> blow up on tier L, where we fall back to "
     "kernelisation and report a timeout."),
    ("I. Nearest sites and checksums",
     "n sites with integer x, y: the pair at minimum squared Euclidean distance. Two long decimals (concatenated "
     "8-digit serials, up to 8n digits): their product.",
     "Closest pair: brute force O(n<super>2</super>), divide and conquer O(n log n); multiplication: schoolbook "
     "O(d<super>2</super>), Karatsuba O(d<super>1.585</super>).",
     "<b>Primary:</b> divide and conquer closest pair; Karatsuba on digit arrays. <b>Baseline:</b> brute force pair "
     "and schoolbook; Python big-int is used only to verify.",
     "Sites are distinct integers, so exact arithmetic avoids float ties. Trap 46 gives about 14k-digit numbers, where "
     "Karatsuba wins. Below about 64 digits Karatsuba is slower, so we switch to schoolbook there."),
]


def build_proposal(path):
    doc = SimpleDocTemplate(path, pagesize=landscape(A4), leftMargin=9 * mm, rightMargin=9 * mm,
                            topMargin=8 * mm, bottomMargin=8 * mm,
                            title="LIFELINE proposal", author=f"Group {CFG['group']}")
    head = [P(h, cellb) for h in ("Module", "Problem", "Candidates", "Selection", "Justification")]
    rows = [head] + [[P(f"<b>{m}</b>", cell), P(a, cell), P(b, cell), P(c, cell), P(d, cell)]
                     for m, a, b, c, d in MODULES]
    w = landscape(A4)[0] - 18 * mm
    t = Table(rows, colWidths=[w * 0.09, w * 0.21, w * 0.24, w * 0.19, w * 0.27], repeatRows=1)
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#d9d9d9")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 1.6), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.6),
        ("LEFTPADDING", (0, 0), (-1, -1), 2.5), ("RIGHTPADDING", (0, 0), (-1, -1), 2.5),
    ]))
    contrib = [
        "<b>Data modules:</b> locations, roads, closure waves, the Landslide corridor builder and trap 48. "
        "<b>Validator:</b> V3 references, V4 connectivity and waves, signature rules of studies 1 and 5, "
        "variety rule 2. <b>Claims:</b> none (network has no claim); reviewed cargo_opt. "
        "<b>Approach note:</b> part 1 (story to numbers). <b>Proposes for Iteration 2:</b> B Route planning, "
        "F Network planning, I Nearest sites and checksums.",
        "<b>Data modules:</b> crates and capacity, windows, incidents, safety rules and assignment, rations, "
        "traps 46 and 47. <b>Validator:</b> V2 ranges, V6 planted assignment and rations, signature rules of "
        "studies 2, 4 and 6, variety rules 1 and 3. <b>Claims:</b> cargo_opt, window_count_opt, window_value_opt. "
        "<b>Approach note:</b> part 2 (planted objects). <b>Proposes:</b> A Relief inventory, C Rescue "
        "scheduling, D Emergency queue, H (SAT and subset sum).",
        "<b>Data modules:</b> radio log, patterns, reports, sites and tour, pipeline, drum, sensor graph and cover, "
        "trap 49, the workbook writer. <b>Validator:</b> V1 structure, V5 pattern counts, edit bound and claims, "
        "V8 traps, the broken test copies and validation_report.txt. <b>Claims:</b> drum_opt, tour_opt, "
        "cover_min. <b>Approach note:</b> parts 3-4. <b>Proposes:</b> E Radio logs, G Chains and cuts, H (TSP "
        "and vertex cover).",
    ]
    rows2 = [[P("Member", cellb), P("Contribution", cellb)]]
    big = ParagraphStyle("c2", parent=cell, fontSize=9.5, leading=12)
    for m, c in zip(MEM, contrib):
        rows2.append([P(f"{m['name']}<br/>{m['roll']}<br/>Section {m['section']}", big), P(c, big)])
    t2 = Table(rows2, colWidths=[w * 0.18, w * 0.82])
    t2.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#d9d9d9")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    doc.build([t, PageBreak(), t2])


def main():
    build_approach(os.path.join(ROOT, "approach_note.pdf"))
    build_proposal(os.path.join(ROOT, "proposal.pdf"))
    with open(os.path.join(ROOT, "members.txt"), "w", newline="\n") as fh:
        fh.write(f"Group number: {CFG['group']}\n")
        for m in MEM:
            fh.write(f"{m['name']}, {m['roll']}, Section {m['section']}\n")
    with open(os.path.join(ROOT, "repository.txt"), "w", newline="\n") as fh:
        fh.write(f"https://github.com/{CFG['github_user']}/{NAME}\n")
    print("built approach_note.pdf, proposal.pdf, members.txt, repository.txt; submission name:", NAME)


if __name__ == "__main__":
    main()
