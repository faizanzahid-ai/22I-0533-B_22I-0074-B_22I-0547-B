# LIFELINE: Algorithmic Relief-Command Engine
## Iteration 1: Approach Note — Data Generation, Planted Witnesses, and Algorithmic Hardness

---

### Part 1: From Story to Numbers

Each of the six case studies models a distinct disaster topology, logistical challenge, and communication environment. The numerical constraints and distributions were derived directly from narrative requirements:

1. **Delta Flood (Case Study 1)**:
   * *Story Justification*: *"A flat delta of small villages joined by raised roads. Roads go under water in waves. Food and water matter most."*
   * *Numerical Formulation*: A flat delta implies planar-like topological connectivity with limited cycles, modeled by an average degree $2E/V \in [2.2, 3.2]$. Rising water submerges road embankments, creating severe transit delays reflected by at least $40\%$ of locations having a transit penalty $\ge 2$ ($p \in \{2, 4, 6\}$). Sequential flooding is modeled by $\ge 3$ distinct closure waves. Humanitarian survival mandates that food (cat 0) and water (cat 1) crates account for at least $55\%$ of all cargo.

2. **Mountain Earthquake (Case Study 2)**:
   * *Story Justification*: *"A valley town with a few roads and almost no alternatives. The injured need medicine and tools. Bursts of urgent calls follow each aftershock."*
   * *Numerical Formulation*: A constrained alpine gorge produces an extremely sparse network with virtually no alternative routes: average degree $2E/V \in [2.0, 2.6]$. Physical trauma and structural collapse prioritize emergency trauma supplies: medicine (cat 2) and extraction tools (cat 3) crates comprise at least $45\%$ of inventory. Aftershocks generate acute distress spikes, requiring alarm priorities to be heavily skewed towards urgency with a mean priority $\ge 6.0$.

3. **Coastal Cyclone (Case Study 3)**:
   * *Story Justification*: *"A port city and fishing villages. Storm surge closes roads in waves. Rescue windows are short and overlap. The radio is full of noise."*
   * *Numerical Formulation*: Rapid coastal inundation necessitates reinforced refuge points, mandating that at least $25\%$ of all locations are designated shelters (type S). Storm surges flood access roads across $\ge 3$ closure waves. Tight tidal and atmospheric cycles produce short, concurrent rescue opportunities: every rescue window overlaps at least 2 other windows on average. Severe storm static generates noisy radio telemetry utilizing at least 30 of the 38 alphabet symbols.

4. **Urban Flash Flood (Case Study 4)**:
   * *Story Justification*: *"A dense city with many alternative routes. Calls arrive faster than anyone can answer them. Rare equipment is available."*
   * *Numerical Formulation*: A dense metropolitan street grid provides high arterial redundancy, modeled by an average degree $2E/V \ge 3.5$. High population density overwhelms relief dispatchers, generating at least $1.5$ alarms per tick on tiers M and L. Urban institutional stockpiles provide specialized disaster technology, ensuring rare equipment (cat 4) constitutes at least $10\%$ of all crates.

5. **Landslide Corridor (Case Study 5)**:
   * *Story Justification*: *"A single mountain highway along a gorge. A collapse cuts off whole communities."*
   * *Numerical Formulation*: Highway topography along a narrow gorge is modeled as a linear backbone: average degree $\le 2.4$, with no node having more than 4 incident roads ($\max deg \le 4$). Farthest settlements lie deep within the canyon, requiring the maximum unweighted road distance from HQ to be at least $\lfloor V/4 \rfloor$. Landslides occur across $\ge 3$ waves, and the union of all waves isolates at least one target location from the depot.

6. **Outbreak Camp (Case Study 6)**:
   * *Story Justification*: *"A relief camp with an outbreak. Medicine and water count and supplies spoil. Radio beacons repeat the same messages."*
   * *Numerical Formulation*: Infectious epidemic containment requires pharmaceuticals and clean hydration: medicine and water crates (cat 2, 1) account for at least $55\%$ of crates. High biological spoilage rates require at least $50\%$ of crates to expire by hour 300. Automated transmission repeaters rebroadcast static beacons, causing a single dominant symbol to occupy at least $25\%$ of the total radio log.

---

### Part 2: Planted Objects and Claims (Correctness by Construction)

To guarantee that NP-hard problems possess valid, verifiable witnesses without relying on heuristic approximations, the generator constructs planted instances analytically:

1. **Planted Tour (Metric Manhattan TSP)**:
   The generator creates a random permutation $P = (0, \pi_1, \pi_2, \dots, \pi_{n-1})$ over all $n$ site coordinates in $[0, 999]^2$. The `tour_length` field is computed by evaluating the closed Manhattan cycle $\sum_{i=0}^{n-1} (|x_{P[i]} - x_{P[(i+1)\%n]}| + |y_{P[i]} - y_{P[(i+1)\%n]}|)$. On Tiers L and X, the planted tour is generated using the Nearest-Neighbor (NN) heuristic starting from site 0. Its length is guaranteed by definition to be no longer than the NN tour. On Tier S ($n \le 9$), the exact optimum `tour_opt` is computed using Held-Karp dynamic programming ($O(n^2 2^n)$).

2. **Planted Sensor Cover (Minimum Vertex Cover)**:
   A target subset $C \subset \{0, \dots, n-1\}$ of size $k \in [2, \lfloor n/2 \rfloor]$ is selected uniformly at random. Every edge $(u, v)$ in `sensor_edges` is constructed such that $\Pr(u \in C \lor v \in C) = 1$. First, all non-cover nodes $\{v \notin C\}$ are connected directly to nodes in $C$. Additional edges are added exclusively between pairs containing at least one member of $C$. Thus, $C$ touches every edge, establishing a valid vertex cover of size $k$ by construction. On Tier S ($n \le 14$), the true minimum cover size `cover_min` is evaluated via exact subset search.

3. **Planted Safety Assignment (3-SAT)**:
   A ground-truth truth assignment $A: \{1, \dots, m\} \to \{0, 1\}$ is generated for the safety switches. For each 3-CNF clause $(l_1 \lor l_2 \lor l_3)$, three distinct switches are sampled. The generator explicitly enforces satisfaction by selecting one switch $s$ and setting its literal to $+s$ if $A[s]=1$ or $-s$ if $A[s]=0$. The remaining two literals are assigned random polarities. Consequently, every clause contains at least one satisfied literal under $A$.

4. **Planted Rations (Exact Subset Sum)**:
   For $m$ ration items with positive integer quantities $v_i \in [1, 1000]$, independent Bernoulli selection bits $b_i \in \{0, 1\}$ are drawn. The target `rations_target` is defined as $\sum_{i=0}^{m-1} b_i v_i$. The planted subset sums to the target by definition.

5. **Tier S Exact Claims**:
   Tier S parameters are intentionally sized ($n \le 20$ crates, $V \le 12$, $n \le 9$ sites, $n \le 14$ sensor nodes) so that exact dynamic programming and branch-and-bound algorithms solve 0/1 knapsack (`cargo_opt`), unweighted interval scheduling (`window_count_opt`), weighted interval scheduling (`window_value_opt`), rod cutting (`drum_opt`), metric TSP (`tour_opt`), and minimum vertex cover (`cover_min`) to global optimality in under 10 milliseconds per case.

---

### Part 3: The Four Trap Cases (Tier X: Cases 46 to 49)

Cases 46 to 49 are deliberately adversarial stress tests designed to induce worst-case computational complexity or trap naive heuristic algorithms:

1. **Case 46: Dock-Order Trap (Study 5 Story)**:
   * *Construction*: 1,600 crates where crate records are pre-sorted such that four fields (`serial`, `expiry`, `weight`, and `value`) are monotonically non-decreasing.
   * *Hostility*: Highly hostile to divide-and-conquer sorting routines. Unbalanced partitioning in Quicksort with first/last element pivot selection degrades to $O(n^2)$ time and exhausts stack frames.
   * *Validator Verification*: Validator check V8 verifies that in `crate_id` order, at least 3 of the 5 fields are monotone.

2. **Case 47: Best-Looking-Crate Trap (Study 6 Story)**:
   * *Construction*: 12 crates and capacity $W = 20$ kg. One bait crate has weight 1 kg and value 12 (value-density ratio 12.0), four optimal crates have weight 20 kg and value 100 (ratio 5.0), and seven filler crates have weight 15 kg and value 10 (ratio 0.67). Total crate weight is 186 kg ($W = 20$ is $10.7\%$, within $[10\%, 70\%]$).
   * *Hostility*: Traps greedy approximation algorithms. Sorting by value-density selects the 1 kg crate first, leaving 19 kg of capacity. None of the 20 kg crates can fit, forcing greedy to take a filler crate for a total value of $12 + 10 = 22$. The true optimum selects a single 20 kg crate for value 100. Greedy achieves only $22\%$ of optimal ($\le 60\%$).
   * *Validator Verification*: Validator check V8 evaluates exact 0/1 knapsack DP vs greedy heuristic and verifies $val_{greedy} \le 0.60 \times val_{opt}$.

3. **Case 48: Shortest-Looks-Cheapest Trap (Study 1 Story)**:
   * *Construction*: 1,600 locations containing a 550-hop linear spine ($0 - 1 - \dots - 550$) ensuring network diameter $\ge 500$ roads. Target 0 connects directly to HQ via a 1-hop highway with traversal time 60 minutes and penalty 6 (cost 66), but an alternative 2-hop detour ($0 \to 554 \to target\_0$) costs only $1 + 1 = 2$ minutes.
   * *Hostility*: Traps breadth-first search and hop-count routing heuristics. The path with the fewest roads has 1 road with cost 66, whereas the cheapest path has 2 roads with cost 2. Every minimum-hop route costs $33.0 \times$ more than the cheapest route ($\ge 1.5 \times$).
   * *Validator Verification*: Validator check V8 verifies diameter $\ge 500$ roads via BFS and verifies that for target 0, the minimum-cost BFS hop path is at least $1.5 \times$ the Dijkstra shortest path.

4. **Case 49: Near-Miss Trap (Study 2 Story)**:
   * *Construction*: 55,000 log symbols where $93\%$ of characters are repetitions of `'A'`. Patterns of length $L \in \{2, 4, 8, 12, 20, 40\}$ are structured with prefixes `'A'*(L - 1)`.
   * *Hostility*: Induces catastrophic backtracking in naive string matching algorithms. Every search position matches $L - 1$ characters before mismatching on the terminal symbol, forcing $O(N \cdot M)$ worst-case character comparisons in naive scan, whereas KMP processes it in strictly linear $O(N + M)$ time.
   * *Validator Verification*: Validator check V8 verifies block repetition $\ge 90\%$ and confirms that for at least 4 patterns, the prefix of length $L - 1$ matches at $\ge 50\%$ of all starting positions.

---

### Part 4: What Will Be Hard in Iteration 2

For each case study, specific data characteristics create acute computational bottlenecks for relief command decisions:

1. **Delta Flood**:
   * *Hardest Decision 1: Route Planning (Module B)*. High prevalence of node penalties ($\ge 40\%$ with $p \ge 2$) combined with disjoint closure waves requires frequent dynamic shortest path recomputation and multi-criteria trade-offs between physical time and risk penalties.
   * *Hardest Decision 2: Network Planning (Module F)*. High road penalties and fluctuating wave closures make finding a stable, minimum-cable spanning tree difficult across waterlogged locations.

2. **Mountain Earthquake**:
   * *Hardest Decision 1: Emergency Queue (Module D)*. Alarm priorities are heavily compressed into the most urgent band ($\bar{p} \ge 6.0$). Under dense aftershock arrivals, numerous incidents share identical peak urgency, requiring multi-level tie-breaking and starvation avoidance.
   * *Hardest Decision 2: Relief Inventory (Module A)*. High demand for bulky extraction tools and medicine crates creates tight knapsack packing constraints where near-optimal packing is critical to prevent medical supply shortages.

3. **Coastal Cyclone**:
   * *Hardest Decision 1: Rescue Scheduling (Module C)*. Dense window clustering where every window overlaps at least two others creates high contention, precluding greedy choices and forcing weighted interval dynamic programming across hundreds of overlapping intervals.
   * *Hardest Decision 2: Radio Logs (Module E)*. Telemetry spans 30+ alphabet symbols with high transmission noise, making error-tolerant edit distance and prefix decoding computationally intensive.

4. **Urban Flash Flood**:
   * *Hardest Decision 1: Emergency Queue (Module D)*. Influx rates exceeding 1.5 alarms per tick on tiers M and L generate substantial queue backlogs, making priority heap maintenance a primary throughput bottleneck.
   * *Hardest Decision 2: Route Planning (Module B)*. High topological density ($2E/V \ge 3.5$) expands the graph branching factor, significantly enlarging Dijkstra's priority queue frontier across Tier L networks (up to 2,000 nodes).

5. **Landslide Corridor**:
   * *Hardest Decision 1: Route Planning (Module B)*. Network depth ($\ge \lfloor V/4 \rfloor$ hops) along a single corridor means that road closures completely isolate downstream sectors, requiring rapid cut-vertex detection and reachability boundary checks.
   * *Hardest Decision 2: Network Planning (Module F)*. Linear canyon topography forces spanning trees to traverse long, fragile paths where single cable segment failures partition the entire downstream relief grid.

6. **Outbreak Camp**:
   * *Hardest Decision 1: Relief Inventory (Module A)*. Over $50\%$ of medical and water crates expire by hour 300. Optimizing truck inventory requires multi-objective scheduling that simultaneously maximizes humanitarian utility and minimizes perishable spoilage loss.
   * *Hardest Decision 2: Radio Logs (Module E)*. Over $25\%$ of log symbols are repetitive beacon characters, skewing frequency tables and requiring efficient run-length and Huffman tree compression to avoid memory bloat.
