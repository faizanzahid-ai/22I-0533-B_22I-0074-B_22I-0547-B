"""
LIFELINE Algorithmic Relief-Command Engine - Proposal PDF Generator
Generates exactly two pages:
Page 1: One table with one row per chosen module (Modules A to I) and nothing else.
Page 2: Work division table with one row per member.
"""

import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import pypdf

def generate_proposal_pdf(output_path="proposal.pdf", group_seed=17, members=None):
    if members is None:
        members = [
            {
                "name": "Ch Faizan Zahid",
                "roll": "22I-0533",
                "section": "BS-AI (B)",
                "contribution": "Iteration 1: Generator architecture, knapsack/claims exact solver (crates, claims sheets), graph generator & closures (roads, waves sheets), validator core engine (V1-V5 checks), approach note part 1 & 2. Proposed Iteration 2 Modules: Module A (Relief Inventory), Module B (Route Planning), Module H (Hard Planning Questions: 3-SAT & TSP)."
            },
            {
                "name": "MOhid Abbas",
                "roll": "24I-0074",
                "section": "BS-AI (B)",
                "contribution": "Iteration 1: Incident & rescue window generators (incidents, windows sheets), radio log & report generators (radio_log, radio_reports sheets), validator checks (V6-V7 signature & variety checks), validator test suite (broken test cases), approach note part 3 & 4. Proposed Iteration 2 Modules: Module C (Rescue Scheduling), Module D (Emergency Queue), Module E (Radio Logs)."
            },
            {
                "name": "Fizan Tariq",
                "roll": "22I-0547",
                "section": "BS-AI (B)",
                "contribution": "Iteration 1: Geometric sites & sensor network generators (sites, tour, sensor_edges, sensor_cover sheets), pipeline & drum generators (pipeline_dims, drum_prices, rations sheets), validator trap checks (V8 checks), validation report compilation, repository & packaging. Proposed Iteration 2 Modules: Module F (Network Planning), Module G (Chains and Cuts), Module I (Nearest Sites and Checksums)."
            }
        ]

    # Letter is 612 x 792 points. Margins: 18 pt left/right, 18 pt top/bottom.
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=16,
        rightMargin=16,
        topMargin=16,
        bottomMargin=16
    )

    styles = getSampleStyleSheet()
    
    # Custom compact paragraph styles
    cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=6.5,
        leading=8.0,
        textColor=colors.black
    )
    
    cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=cell_style,
        fontName='Helvetica-Bold',
        fontSize=7.0,
        leading=8.5
    )
    
    header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.0,
        textColor=colors.whitesmoke,
        alignment=1 # Center
    )

    story = []

    # =========================================================================
    # PAGE 1: EXACTLY ONE TABLE WITH ONE ROW PER CHOSEN MODULE AND NOTHING ELSE
    # =========================================================================
    p1_headers = [
        Paragraph("<b>Module</b>", header_style),
        Paragraph("<b>Problem (Variables: n, m, V, E, W)</b>", header_style),
        Paragraph("<b>Candidates (with Complexity)</b>", header_style),
        Paragraph("<b>Selection (Primary vs Baseline)</b>", header_style),
        Paragraph("<b>Justification (Data Property, Assumptions & Failure Case)</b>", header_style)
    ]

    modules_data = [
        (
            "A. Relief inventory",
            "<b>0/1 Knapsack</b>. Input: n crates with weights w_i in [1, 20] kg, values v_i in [10, 100], truck capacity W <= sum(w_i). Output: Set S subset {1..n} maximizing total value sum(v_i) subject to total weight sum(w_i) <= W.",
            "1. <b>1D Tabular DP</b>: O(n * W) pseudo-poly.<br/>2. <b>Branch and Bound</b>: O(2^n) worst-case.<br/>3. <b>Greedy by v/w ratio</b>: O(n log n).",
            "<b>Primary:</b> 1D Dynamic Programming O(n * W).<br/><b>Baseline:</b> Greedy value-density heuristic O(n log n).",
            "Weights and capacity are strictly positive integers with W <= 30,000, where pseudo-polynomial DP runs in milliseconds. Assumes static integer crate weights. Fails if weights/capacities are continuous non-integral reals or capacity W >> 10^7."
        ),
        (
            "B. Route planning",
            "<b>Single-Source Shortest Paths & Reachability</b>. Input: Directed graph G=(V, E) with road traversal time minutes(e) in [1, 60] and destination penalty(v) in {0,1,2,4,6}. Output: Cheapest path minimizing sum(minutes + penalty_v), reachable set, and min-hop path.",
            "1. <b>Dijkstra with Min-Heap</b>: O((V + E) log V).<br/>2. <b>Bellman-Ford</b>: O(V * E).<br/>3. <b>Unweighted BFS</b>: O(V + E) for hop count.",
            "<b>Primary:</b> Dijkstra with Min-Heap O((V+E)log V) and BFS O(V+E).<br/><b>Baseline:</b> Bellman-Ford O(V * E).",
            "Minutes and penalties are non-negative (edge cost >= 1), perfectly satisfying Dijkstra's greedy non-negative edge invariant. Assumes static road state per day. Fails if negative cost edges or negative penalty-relief cycles exist."
        ),
        (
            "C. Rescue scheduling",
            "<b>Interval Scheduling & Weighted Interval Scheduling</b>. Input: m rescue windows [start_i, finish_i] with values v_i. Output: Maximum cardinality compatible set (touching allowed) or maximum value compatible set.",
            "1. <b>Greedy Earliest Finish Time (EFT)</b>: O(m log m).<br/>2. <b>Weighted Interval DP with Bisect</b>: O(m log m).<br/>3. <b>Integer Linear Program</b>: O(2^m).",
            "<b>Primary:</b> Greedy EFT for count; DP + Binary Search for value O(m log m).<br/><b>Baseline:</b> Recursive search O(2^m).",
            "Intervals are 1D continuous segments [0, 1440]. Sorted finish times guarantee the greedy-choice property for count and optimal substructure for weighted DP via binary search predecessor lookup. Fails if windows require multi-crew matching or have setup dependencies."
        ),
        (
            "D. Emergency queue",
            "<b>Dynamic Priority Queue Simulation</b>. Input: A alarms arriving at non-decreasing tick t_i with priority p_i in [1, 10] (10 most urgent). Output: Release order answering one alarm per tick in urgency order among available alarms.",
            "1. <b>Dial's Bucket Queue / Multi-level Array</b>: O(A + K) where K=10.<br/>2. <b>Binary Max-Heap</b>: O(A log A).<br/>3. <b>Unsorted Scan</b>: O(A^2).",
            "<b>Primary:</b> Dial's Multi-level Bucket Queue O(A) total, O(1) amortized.<br/><b>Baseline:</b> Binary Max-Heap O(A log A).",
            "Priority values are small, discrete integers bounded in [1, 10]. Direct array buckets permit O(1) insertion and O(1) extraction of the highest-priority incident. Fails if priorities are arbitrary continuous real numbers or priority space K >> A."
        ),
        (
            "E. Radio logs",
            "<b>Exact Pattern Search, String Edit Distance & Data Compression</b>. Input: Alphabet Sigma (|Sigma|=38), log length N, reports of lengths L_a, L_b. Output: All phrase occurrences, min edit script (ins/del/sub), and optimal prefix-free code.",
            "1. <b>Knuth-Morris-Pratt (KMP)</b>: O(N + M) search.<br/>2. <b>Wagner-Fischer DP</b>: O(L_a * L_b) edit dist.<br/>3. <b>Huffman Greedy Tree</b>: O(|Sigma| log |Sigma|).",
            "<b>Primary:</b> KMP search O(N+M), Wagner-Fischer DP O(L_a L_b), Huffman O(|Sigma| log |Sigma|).<br/><b>Baseline:</b> Naive search O(N*M).",
            "Fixed discrete alphabet (|Sigma|=38) and static log text allow linear deterministic automata / failure function preprocessing. Character frequencies in logs exhibit strong skewness (e.g. Study 6 and Trap 49), guaranteeing Huffman optimality. Fails under wildcard / regex stream queries."
        ),
        (
            "F. Network planning",
            "<b>Minimum Spanning Tree (MST)</b>. Input: Connected reachable graph G=(V, E) with cable costs c_e in [1, 100]. Output: Minimum cable cost acyclic subgraph connecting all reachable locations.",
            "1. <b>Kruskal with DSU & Counting Sort</b>: O(E * alpha(V)).<br/>2. <b>Prim with Binary Heap</b>: O(E log V).<br/>3. <b>Boruvka's Algorithm</b>: O(E log V).",
            "<b>Primary:</b> Kruskal with Disjoint Set Union (DSU) O(E * alpha(V)).<br/><b>Baseline:</b> Prim's Algorithm O(E log V).",
            "Road network is relatively sparse (E <= 3V) and cable costs are integers in [1, 100]. Edge weights can be sorted in linear O(E) time using Counting Sort, reducing Kruskal to nearly O(E). Fails on dense graphs where E = Theta(V^2) and Prim with dense matrix is O(V^2)."
        ),
        (
            "G. Chains and cuts",
            "<b>Matrix Chain Multiplication (MCM) & Rod Cutting</b>. Input: n pipeline stage dimensions; drum length L with price array P[1..L]. Output: Optimal associative parenthesization minimizing scalar multiplications; optimal cutting maximizing total revenue.",
            "1. <b>Bottom-up Dynamic Programming</b>: O(n^3) MCM, O(L^2) Rod Cut.<br/>2. <b>Memoized Recursion</b>: O(n^3) MCM, O(L^2) Rod Cut.<br/>3. <b>Greedy Heuristic</b>: O(n log n) MCM.",
            "<b>Primary:</b> Tabular Dynamic Programming O(n^3) MCM, O(L^2) Rod Cut.<br/><b>Baseline:</b> Greedy dimensional / density heuristic.",
            "Both problems possess strict optimal substructure and overlapping subproblems without cyclic dependencies. Stage counts (n <= 300) and drum lengths (L <= 2000) evaluate rapidly under tabular DP. Fails if drum cutting incurs cutting kerf material loss or stage operators are non-associative."
        ),
        (
            "H. Hard planning questions",
            "<b>NP-Hard Combinatorial Decision Problems</b>: 3-SAT (Safety), Exact Subset Sum (Rations), Metric TSP (Tour), and Minimum Vertex Cover (Sensors). Output: Exact satisfying assignment, exact target subset, shortest tour, and min cover.",
            "1. <b>CDCL / DPLL with Unit Propagation</b> for 3-SAT.<br/>2. <b>Meet-in-the-Middle / DP</b>: O(2^(n/2)) or O(n * Target).<br/>3. <b>Held-Karp DP</b> O(n^2 2^n) / <b>2-Opt</b>.<br/>4. <b>FPT Branch & Bound</b>: O(1.2738^k + kn).",
            "<b>Primary:</b> CDCL for 3-SAT, Meet-in-the-Middle for Rations, Held-Karp (Tier S) / 2-Opt (L/X) for TSP, FPT B&B for MVC.<br/><b>Baseline:</b> Brute-force O(2^n) / O(n!).",
            "Planted solutions exist by construction (planted cover k <= n/2, planted assignment, planted subset). Small parameter sizes on Tier S (n <= 15) allow exact Held-Karp / FPT algorithms to verify claims. Fails on unconstrained instances beyond the 3-SAT phase transition ratio (rules/vars ~ 4.267)."
        ),
        (
            "I. Nearest sites and checksums",
            "<b>2D Closest Pair of Points & Arbitrary-Precision Multiplication</b>. Input: n coordinates (x, y) in [0, 999]^2; two long decimal numbers from concatenated crate serials (d digits). Output: Minimum squared Euclidean distance; high-precision product.",
            "1. <b>Divide and Conquer Closest Pair</b>: O(n log n).<br/>2. <b>Karatsuba Multiplication</b>: O(d^1.585).<br/>3. <b>Naive Pairwise & Schoolbook</b>: O(n^2) and O(d^2).",
            "<b>Primary:</b> Divide-and-Conquer Closest Pair O(n log n) and Karatsuba O(d^1.585).<br/><b>Baseline:</b> Pairwise distance O(n^2) and Schoolbook multiplication O(d^2).",
            "Sites lie in a bounded Euclidean plane where recursive geometric strip pruning guarantees at most 7 candidates per point; serial digit lengths d reach thousands of digits in Tier L where Karatsuba achieves substantial sub-quadratic speedup. Fails for points in high dimensions (D >> 10)."
        )
    ]

    p1_rows = [p1_headers]
    for m_label, prob, cands, sel, just in modules_data:
        p1_rows.append([
            Paragraph(f"<b>{m_label}</b>", cell_bold),
            Paragraph(prob, cell_style),
            Paragraph(cands, cell_style),
            Paragraph(sel, cell_style),
            Paragraph(just, cell_style)
        ])

    # Table dimensions: Total width = 612 - 32 = 580 pt.
    # Col widths: Module(70), Problem(125), Candidates(115), Selection(115), Justification(155) -> Total = 580
    col_widths_p1 = [70, 125, 115, 115, 155]
    table_p1 = Table(p1_rows, colWidths=col_widths_p1, repeatRows=1)
    table_p1.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1A365D')), # Deep Navy
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')])
    ]))

    story.append(table_p1)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 2: WORK DIVISION TABLE (ONE ROW PER MEMBER AND NOTHING ELSE)
    # =========================================================================
    p2_cell_style = ParagraphStyle(
        'P2Cell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.black
    )
    p2_cell_bold = ParagraphStyle(
        'P2CellBold',
        parent=p2_cell_style,
        fontName='Helvetica-Bold',
        fontSize=9.0,
        leading=12.0
    )
    p2_header_style = ParagraphStyle(
        'P2Header',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.0,
        leading=13.0,
        textColor=colors.whitesmoke,
        alignment=1
    )

    p2_headers = [
        Paragraph("<b>Member</b>", p2_header_style),
        Paragraph("<b>Contribution (Iteration 1 Deliverables & Proposed Iteration 2 Modules)</b>", p2_header_style)
    ]

    p2_rows = [p2_headers]
    for mem in members:
        mem_info = f"<b>{mem['name']}</b><br/>Roll No: {mem['roll']}<br/>Section: {mem['section']}"
        p2_rows.append([
            Paragraph(mem_info, p2_cell_bold),
            Paragraph(mem['contribution'], p2_cell_style)
        ])

    # Col widths: Member(150), Contribution(430) -> Total = 580 pt.
    col_widths_p2 = [150, 430]
    table_p2 = Table(p2_rows, colWidths=col_widths_p2, repeatRows=1)
    table_p2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1A365D')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 16),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 16),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')])
    ]))

    story.append(table_p2)

    doc.build(story)

    # Verify exact page count using pypdf
    reader = pypdf.PdfReader(output_path)
    page_count = len(reader.pages)
    print(f"Generated {output_path} with {page_count} pages.")
    assert page_count == 2, f"Proposal PDF must be exactly 2 pages, found {page_count}!"

if __name__ == "__main__":
    generate_proposal_pdf()
