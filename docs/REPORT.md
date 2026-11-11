# Smart Courier Planner - Final Report

**Student:** Ayush Kumar Nayak | **Roll No.:** 2501730071 | B.Tech CSE (AI & ML), Sem 3, Section C

## 1. Objective
Build a prototype that, given parcels and delivery points, produces an ordered delivery route and
an optimised packing plan, integrating sorting, dynamic programming, graph algorithms and an
approximation technique, and measure the runtime of each part.

## 2. Implementation summary
Python 3 with only the standard library plus matplotlib for charts. Code is split by algorithm
(`src/sorting.py`, `knapsack.py`, `graph_routing.py`); `main.py` runs the full pipeline; `src/benchmark.py`
runs the experiments; `tests/` holds 9 unit tests (all pass, see `outputs/test_results.txt`).

## 3. Phase 2 results - prioritisation and packing (small dataset, 40 kg van)
* Merge Sort with key (priority, deadline, -value) ranked 12 parcels; top three are P01, P02, P09 (all priority 1).
* Knapsack DP table: 13 rows x 41 columns (`outputs/small_dp_table.csv`).
* Selected parcels: **P01, P02, P09, P07, P08, P12** - total weight 40/40 kg, total value **330**.
* Greedy filling in sorted order only reaches value 300, so DP gains 30 (10%).
* Large dataset (40 parcels, 60 kg): DP value 924 vs greedy 629 (DP +47%).

## 4. Phase 3 results - graph processing and route
* Dijkstra gives shortest road distance from the warehouse to each stop, e.g. W -> node 1 = 6.8 km via 0-9-2-1.
* Nearest-Neighbour tour (small): W -> 9 -> 2 -> 1 -> 8 -> 7 -> W = **20.5 km**.
  Brute-force check over the 5 stops gives the same 20.5 km, ratio 1.000.
* Large dataset: 13 stops, route length **127.4 km**, trip time about 5.3 h.
* Deadline check: small dataset 0 late; large dataset 3 of 14 parcels late
  (P026, P011, P008) because nearest-neighbour ignores deadlines.

## 5. Phase 4 - runtime results (from `outputs/runtime_results.csv`, one machine, median of 3 runs)
| Step | Input size | Time | Observation |
|---|---|---|---|
| Merge sort | n = 100 / 2000 / 4000 | 0.09 / 2.8 / 6.1 ms | doubling n slightly more than doubles time: O(n log n) |
| Quick sort | n = 4000 | 8.0 ms | similar to merge sort on random data |
| Insertion sort | n = 2000 / 4000 | 64.6 / 268 ms | doubling n gives about 4x: O(n^2) |
| Knapsack DP (C = 500) | n = 100 / 200 / 400 | 4.3 / 8.4 / 17.6 ms | doubling n doubles time: O(nC) |
| Dijkstra (one source) | V = 200 / 2000 | 0.14 / 3.0 ms | near-linear growth, O((V+E) log V) |
| NN tour (after matrix) | k = 100 / 200 / 400 | 0.42 / 2.4 / 10.9 ms | doubling k gives about 4x: O(k^2) |

Charts: `outputs/runtime_chart.png`. Python's built-in `sorted` is faster than my merge sort because it
is written in C - my implementation is for demonstrating the algorithm.

**Approximation quality** (`outputs/quality_chart.png`): on 15 random networks per k, NN / optimum averaged
1.03-1.11 for k = 4..9; the worst single case was 1.405 (k = 8). So the heuristic is usually within about
10% but can be 40% worse than optimal.

## 6. Optimisation suggestions for future work
1. Run Dijkstra once per stop only for the stops that are needed (already done) and cache matrices across trips.
2. Improve the NN tour with **2-opt** swaps to remove crossing paths.
3. Make the route **deadline-aware**: order or insert stops by deadline (time-window TSP) to remove late parcels.
4. Reduce knapsack memory from O(nC) to O(C) with a 1-D array if the table does not need printing.
5. Use A* with coordinates as heuristic for very large road networks.
6. Let the knapsack consider route cost (nearby parcels are cheaper to deliver) instead of value alone.
7. Loop trips: after trip 1, repeat the pipeline on the remaining parcels until all are delivered.

## 7. Limitations
Single van, one trip; fixed average speed; volume of parcels is ignored (weight only); nearest-neighbour has
no worst-case guarantee on general graphs; benchmark times depend on the machine.

## 8. Conclusion
All four techniques work together: merge sort ranks parcels, DP selects the best load, Dijkstra supplies
true road distances, and nearest-neighbour builds a good (not always optimal) route. Measured runtimes match the
theoretical complexities, and tests confirm correctness.

## 9. Evidence files
`outputs/small_run_log.txt`, `large_run_log.txt`, `small_dp_table.csv`, `small_route.png`, `large_route.png`,
`runtime_chart.png`, `quality_chart.png`, `runtime_results.csv`, `quality_results.csv`, `test_results.txt`.
