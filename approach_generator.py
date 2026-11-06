"""
Compile approach.md into an elegant, exactly two-page PDF (approach.pdf).
"""

import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, KeepTogether, Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import pypdf

def generate_approach_pdf(output_path="approach.pdf"):
    # Letter: 612 x 792 pt
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=24,
        rightMargin=24,
        topMargin=20,
        bottomMargin=20
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'AppTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#0F172A'),
        alignment=1 # Center
    )

    sub_style = ParagraphStyle(
        'AppSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#475569'),
        alignment=1
    )

    h1_style = ParagraphStyle(
        'AppH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=12.5,
        textColor=colors.HexColor('#1E3A8A'),
        spaceBefore=4,
        spaceAfter=2
    )

    h2_style = ParagraphStyle(
        'AppH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.8,
        leading=10,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=2,
        spaceAfter=1
    )

    body_style = ParagraphStyle(
        'AppBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.2,
        leading=9.2,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=2.5
    )

    story = []

    # Title Banner
    story.append(Paragraph("<b>LIFELINE: Algorithmic Relief-Command Engine</b>", title_style))
    story.append(Paragraph("Iteration 1 Approach Note: Data Generation, Planted Objects, Adversarial Traps & Computational Complexity", sub_style))
    story.append(Spacer(1, 4))

    # --- PART 1 ---
    story.append(Paragraph("<b>1. From Story to Numbers: Narrative Calibration & Parameter Choices</b>", h1_style))
    p1_items = [
        ("Delta Flood (Study 1)", "Story: 'A flat delta of small villages joined by raised roads. Roads go under water in waves. Food and water matter most.'",
         "Topological planar connectivity is modeled with average degree 2E/V in [2.2, 3.2]. Flooding is modeled by over 40% of locations having high traversal penalties >= 2 (p in {2, 4, 6}) and at least 3 closure waves. Food (cat 0) and water (cat 1) crates account for >= 55% of inventory."),
        ("Mountain Earthquake (Study 2)", "Story: 'A valley town with a few roads and almost no alternatives. The injured need medicine and tools. Bursts of urgent calls follow each aftershock.'",
         "Alpine valley geography constrains network topology to a sparse backbone with almost no alternative cycles: average degree 2E/V in [2.0, 2.6]. Physical trauma prioritizes medicine (cat 2) and rescue tools (cat 3) crates (>= 45%). Aftershock bursts generate severe urgency spikes, requiring mean alarm priority >= 6.0."),
        ("Coastal Cyclone (Study 3)", "Story: 'A port city and fishing villages. Storm surge closes roads in waves. Rescue windows are short and overlap. The radio is full of noise.'",
         "Rapid inundation mandates evacuation refuge: >= 25% of locations are shelters (type S). Road closures occur across >= 3 waves. Tight tidal cycles produce short, heavily clustered rescue windows where every window overlaps at least 2 other windows on average. Severe storm static uses >= 30 of the 38 radio alphabet symbols."),
        ("Urban Flash Flood (Study 4)", "Story: 'A dense city with many alternative routes. Calls arrive faster than anyone can answer them. Rare equipment is available.'",
         "Dense metropolitan grid provides high arterial redundancy: average degree 2E/V >= 3.5. Overwhelmed dispatchers experience >= 1.5 alarms per tick on tiers M and L. Municipal stockpiles provide specialized disaster technology, ensuring rare equipment (cat 4) comprises >= 10% of crates."),
        ("Landslide Corridor (Study 5)", "Story: 'A single mountain highway along a gorge. A collapse cuts off whole communities.'",
         "Canyon gorge restricts roads to a linear chain without bypasses: average degree <= 2.4, and no location has > 4 incident roads. Depth into the corridor requires unweighted distance to the farthest settlement to be >= floor(V/4) roads. Mass wasting occurs across >= 3 waves, and the union of all waves severs all paths to at least one target location from HQ."),
        ("Outbreak Camp (Study 6)", "Story: 'A relief camp with an outbreak. Medicine and water count and supplies spoil. Radio beacons repeat the same messages.'",
         "Infectious containment requires clean hydration and treatments: medicine and water crates (cat 2, 1) account for >= 55% of crates. Biological spoilage forces >= 50% of crates to expire by hour 300. Automated transmission repeaters rebroadcast static beacons, causing a single dominant symbol to occupy >= 25% of the total radio log.")
    ]
    for title, quote, desc in p1_items:
        story.append(Paragraph(f"<b>{title}:</b> <i>{quote}</i> — {desc}", body_style))

    # --- PART 2 ---
    story.append(Spacer(1, 3))
    story.append(Paragraph("<b>2. Planted Objects & Claims: Exact Correctness by Construction</b>", h1_style))
    p2_items = [
        ("Planted Metric Manhattan Tour (TSP)", "A closed permutation starting at site 0 is generated over all n coordinates in [0, 999]^2. Its length is evaluated as the closed Manhattan cycle sum. On Tiers L and X, the tour is constructed using the Nearest-Neighbor (NN) heuristic starting from 0, guaranteeing length <= NN tour length by definition. On Tier S (n <= 9), the global optimum tour_opt is evaluated via Held-Karp dynamic programming O(n^2 2^n)."),
        ("Planted Vertex Cover (MVC)", "A target subset C of size k in [2, floor(n/2)] is chosen. Every edge in sensor_edges is generated such that at least one endpoint is in C. All non-cover nodes are connected directly to C, and internal edges only connect pairs with at least one cover node. Thus, C is a valid vertex cover of size k by construction. On Tier S, the exact minimum cover size cover_min is evaluated via exact subset search."),
        ("Planted Safety Assignment (3-SAT)", "A ground-truth truth assignment A is chosen for switches 1..m. Each 3-CNF clause is constructed by selecting one literal that evaluates to True under A (+s if A[s]=1, -s if A[s]=0). The other two literals are assigned random polarities. Consequently, every clause is guaranteed to be satisfied by A."),
        ("Planted Rations (Exact Subset Sum)", "For m ration items with quantities v_i in [1, 1000], random binary selection flags b_i in {0, 1} are drawn. The target rations_target is set to sum(b_i * v_i). The planted subset sums exactly to target by construction."),
        ("Tier S Exact Claims", "For cases 00 to 19, exact algorithms solve 0/1 knapsack (cargo_opt), unweighted interval scheduling (window_count_opt), weighted interval scheduling (window_value_opt), rod cutting (drum_opt), metric TSP (tour_opt), and minimum vertex cover (cover_min) to provable global optimality.")
    ]
    for title, desc in p2_items:
        story.append(Paragraph(f"<b>{title}:</b> {desc}", body_style))

    # Page 1 ends cleanly here!
    story.append(PageBreak())

    # =========================================================================
    # PAGE 2: PART 3 & PART 4
    # =========================================================================
    story.append(Paragraph("<b>3. The Four Trap Cases (Tier X: Cases 46 to 49)</b>", h1_style))
    p3_items = [
        ("Case 46: Dock-Order Trap (Study 5 Story)", "1,600 crates pre-sorted such that serial, expiry, weight, and value are monotonically non-decreasing.",
         "Hostile to divide-and-conquer sorting routines. Unbalanced partitioning in Quicksort with first/last element pivot selection degrades to worst-case O(n^2) time and risks recursion stack exhaustion.",
         "Validator check V8 verifies that in crate_id order, at least 3 of the 5 fields are monotone."),
        ("Case 47: Best-Looking-Crate Trap (Study 6 Story)", "12 crates and capacity W = 20 kg. One bait crate has weight 1 kg, value 12 (ratio 12.0); four optimal crates have weight 20 kg, value 100 (ratio 5.0); seven filler crates have weight 15 kg, value 10 (ratio 0.67). Total crate weight is 186 kg (W = 20 is 10.7%, in [10%, 70%]).",
         "Traps greedy value-density heuristics. Sorting by value-density selects the 1 kg crate first, leaving 19 kg of capacity. None of the 20 kg crates can fit, forcing greedy to take a filler crate for total value 12 + 10 = 22. The true optimum selects a single 20 kg crate for value 100. Greedy achieves only 22% of optimal (<= 60%).",
         "Validator check V8 evaluates exact 0/1 knapsack DP vs greedy heuristic and verifies val_greedy <= 0.60 * val_opt."),
        ("Case 48: Shortest-Looks-Cheapest Trap (Study 1 Story)", "1,600 locations containing a 550-hop linear spine (0 - 1 - ... - 550) ensuring diameter >= 500 roads. Target 0 connects to HQ via a 1-hop direct highway with traversal time 60 min and penalty 6 (cost 66), but an alternative 2-hop detour (0 -> 554 -> target_0) costs only 1 + 1 = 2 min.",
         "Traps breadth-first search and hop-count heuristics. The path with the fewest roads has 1 road with cost 66, whereas the cheapest path has 2 roads with cost 2. Every minimum-hop route costs 33.0x more than the cheapest route (>= 1.5x).",
         "Validator check V8 verifies network diameter >= 500 roads via BFS and verifies that for target 0, the minimum-cost BFS hop path is at least 1.5x the Dijkstra shortest path."),
        ("Case 49: Near-Miss Trap (Study 2 Story)", "55,000 log symbols where 93% of characters are repetitions of 'A'. Patterns of length L in {2, 4, 8, 12, 20, 40} are structured with prefixes 'A'*(L - 1).",
         "Induces catastrophic backtracking in naive string matching algorithms. Every search position matches L - 1 characters before mismatching on the terminal symbol, forcing O(N * M) worst-case comparisons in naive scan, whereas KMP processes it in strictly linear O(N + M) time.",
         "Validator check V8 verifies block repetition >= 90% and confirms that for at least 4 patterns, the prefix of length L - 1 matches at >= 50% of all start positions.")
    ]
    for title, constr, host, vchk in p3_items:
        story.append(Paragraph(f"<b>{title}:</b> <b>Built:</b> {constr} <b>Hostility:</b> {host} <b>Validator Check:</b> {vchk}", body_style))

    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>4. What Will Be Hard in Iteration 2: Bottlenecks & Algorithmic Hardness</b>", h1_style))
    p4_items = [
        ("Delta Flood", "<b>Route Planning (Module B):</b> High road penalties (>= 40% with p >= 2) combined with multi-wave dynamic closures require continuous re-routing and multi-criteria optimization between physical travel time and hazard exposure penalties.<br/><b>Cable Network Planning (Module F):</b> Spanning tree construction must navigate waterlogged locations with severe cable weights across dynamically severed road networks."),
        ("Mountain Earthquake", "<b>Emergency Queue (Module D):</b> Alarm priorities are heavily compressed into the peak urgency band (mean priority >= 6.0). Under dense aftershocks, numerous incidents share identical priority, requiring multi-level tie-breaking and starvation prevention.<br/><b>Relief Inventory (Module A):</b> High demand for heavy extraction tools and medical crates creates tight packing constraints where near-optimal knapsack solutions are critical."),
        ("Coastal Cyclone", "<b>Rescue Scheduling (Module C):</b> Severe interval contention where every rescue window overlaps at least two others precludes greedy choice, requiring weighted interval dynamic programming across hundreds of overlapping intervals.<br/><b>Radio Logs (Module E):</b> Telemetry spans 30+ alphabet symbols with high atmospheric noise, making error-tolerant edit distance and prefix decoding computationally intensive."),
        ("Urban Flash Flood", "<b>Emergency Queue (Module D):</b> Influx rates exceeding 1.5 alarms per tick on tiers M and L generate large queue backlogs, making priority heap maintenance a throughput bottleneck.<br/><b>Route Planning (Module B):</b> High topological density (2E/V >= 3.5) expands the graph branching factor, significantly enlarging Dijkstra's priority queue frontier across Tier L networks (up to 2,000 nodes)."),
        ("Landslide Corridor", "<b>Route Planning (Module B):</b> Network depth (>= floor(V/4) hops) along a single corridor means road closures cause complete community isolation, requiring rapid articulation-point detection and reachability boundary checks.<br/><b>Network Planning (Module F):</b> Linear canyon topography forces spanning trees along fragile paths where single cable segment failures partition the entire downstream relief grid."),
        ("Outbreak Camp", "<b>Relief Inventory (Module A):</b> Over 50% of medical and water crates expire by hour 300. Optimizing truck inventory requires multi-objective scheduling that simultaneously maximizes humanitarian utility and minimizes perishable spoilage loss.<br/><b>Radio Logs (Module E):</b> Over 25% of log symbols are repetitive beacon characters, skewing frequency tables and requiring efficient run-length and Huffman tree compression to avoid memory bloat.")
    ]
    for title, desc in p4_items:
        story.append(Paragraph(f"<b>{title}:</b> {desc}", body_style))

    doc.build(story)

    reader = pypdf.PdfReader(output_path)
    page_count = len(reader.pages)
    print(f"Generated {output_path} with {page_count} pages.")
    assert page_count == 2, f"Approach PDF must be exactly 2 pages, found {page_count}!"

if __name__ == "__main__":
    generate_approach_pdf()
