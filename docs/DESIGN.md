# Phase 1 - Courier Problem Design and Planning

## 1. Problem statement
A courier van leaves a warehouse with a limited load capacity. Many parcels are waiting,
each with a destination, weight, value, priority and deadline. The van can carry only some of
them in one trip. The system must decide **which parcels to load**, **in which order the
customers are visited**, and **how fast the algorithms run** as the problem grows.

## 2. Parcel attributes
| Attribute | Type | Meaning |
|---|---|---|
| pid | text | unique parcel id |
| dest | int | graph node where it is delivered |
| weight | int (kg) | uses van capacity |
| value | int | business value score (higher = more important to ship) |
| priority | 1-3 | 1 urgent, 2 normal, 3 low |
| deadline_h | hours | latest delivery time from trip start |

## 3. Graph format
Undirected weighted graph. Nodes = warehouse (id 0) + customer areas + junctions. Edge weight =
road length in km. Stored as an adjacency list `{node: [(neighbour, km), ...]}`
(good for sparse road networks: memory O(V+E)). CSV files are described in the README.

## 4. Algorithm selection and justification
| Need | Chosen algorithm | Reason | Alternatives rejected |
|---|---|---|---|
| Rank parcels by urgency | Merge Sort | O(n log n) worst case, stable, tuple key (priority, deadline, -value) | Quick sort (O(n^2) worst, unstable), insertion sort (O(n^2)) |
| Pick parcels for one trip | 0/1 Knapsack DP | each parcel is taken whole or not at all; DP gives the exact optimum; greedy does not | Greedy (not optimal), brute force (2^n) |
| Road distances | Dijkstra with heap | edge weights are non-negative; works on a sparse graph | Bellman-Ford (slower, not needed), BFS (ignores weights) |
| Visiting order | Nearest-Neighbour TSP | TSP is NP-hard; heuristic is O(k^2) and simple | Brute force (k! orders), only used to check quality for k <= 9 |

## 5. How the parts work together
1. **Sort** all waiting parcels by (priority, deadline, value).
2. **Knapsack** over the sorted list chooses the subset with the highest value that fits the van.
3. The destinations of the chosen parcels + the warehouse are the **stops**.
4. **Dijkstra** runs from every stop; the results form a stop-to-stop distance matrix.
5. **Nearest-Neighbour** builds the tour on that matrix; the stored predecessor maps expand it
   into the full road path; length is summed.
6. A **deadline check** estimates arrival times; **benchmarks** measure each step.

```
+-----------+   +---------+   +-----------+   +----------+   +-------------+
| parcels   |-->| Merge   |-->| Knapsack  |-->| Dijkstra |-->| NN-TSP tour |--> route + km
| + graph   |   | Sort    |   | DP        |   | matrix   |   | + deadlines |
+-----------+   +---------+   +-----------+   +----------+   +-------------+
```

## 6. Evaluation plan (Phase 4)
Runtime of each step for growing input sizes; correctness via unit tests (compared with
Python's `sorted`, brute-force knapsack, hand-made graph); quality of the approximation
(NN length / optimal length for k = 4..9).
