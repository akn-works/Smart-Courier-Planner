"""Smart Courier Planner - runs Phases 2 and 3 of the capstone end to end.

    python main.py                    # small hand-checkable dataset
    python main.py --dataset large    # bigger generated dataset
    python main.py --capacity 30      # change the van capacity (kg)
"""
import argparse
import csv
import os

from src.data_loader import OUT_DIR, load_edges, load_nodes, load_parcels
from src.graph_routing import (brute_force_tour, build_path, distance_matrix,
                               expand_tour, nearest_neighbor_tour, tour_length)
from src.knapsack import greedy_fill, knapsack_01
from src.sorting import merge_sort
from src.visualize import plot_route

DEFAULT_CAPACITY = {"small": 40, "large": 60}
SPEED_KMH = 30.0         # assumed average van speed
SERVICE_MIN = 5.0        # minutes spent at each stop handing over parcels


class Log:
    """Prints a line and also remembers it so it can be saved to outputs/."""
    def __init__(self):
        self.lines = []

    def __call__(self, text=""):
        print(text)
        self.lines.append(text)


def parcel_table(log, parcels):
    log(f"{'Rank':<5}{'ID':<7}{'Dest':<6}{'Wt(kg)':<8}{'Value':<7}{'Prio':<6}{'Deadline(h)':<12}")
    for r, p in enumerate(parcels, 1):
        log(f"{r:<5}{p.pid:<7}{p.dest:<6}{p.weight:<8}{p.value:<7}{p.priority:<6}{p.deadline_h:<12}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="small", choices=["small", "large"])
    ap.add_argument("--capacity", type=int, default=None, help="van capacity in kg")
    args = ap.parse_args()
    name = args.dataset
    capacity = args.capacity or DEFAULT_CAPACITY[name]
    os.makedirs(OUT_DIR, exist_ok=True)
    log = Log()

    nodes = load_nodes(name)
    graph = load_edges(name)
    parcels = load_parcels(name)
    log(f"=== Smart Courier Planner | dataset={name} | parcels={len(parcels)} | "
        f"road nodes={len(nodes)} | van capacity={capacity} kg ===")

    # ---------------- Phase 2a: sort parcels ----------------
    log("\n--- PHASE 2a: Parcel prioritisation (Merge Sort) ---")
    log("Sort key: (priority asc, deadline asc, value desc)")
    ranked = merge_sort(parcels, key=lambda p: (p.priority, p.deadline_h, -p.value))
    parcel_table(log, ranked)

    # ---------------- Phase 2b: knapsack ----------------
    log("\n--- PHASE 2b: Optimal parcel selection (0/1 Knapsack DP) ---")
    weights = [p.weight for p in ranked]
    values = [p.value for p in ranked]
    best, idx, dp = knapsack_01(weights, values, capacity)
    selected = [ranked[i] for i in idx]
    g_val, g_idx = greedy_fill(weights, values, capacity)
    log(f"DP table size: {len(dp)} rows x {len(dp[0])} columns")
    log(f"Selected parcels : {[p.pid for p in selected]}")
    log(f"Total weight     : {sum(p.weight for p in selected)} / {capacity} kg")
    log(f"Total value (DP) : {best}")
    log(f"Greedy-in-sorted-order value for comparison: {g_val}  "
        f"(DP gain = {best - g_val})")
    left = [p.pid for p in ranked if p not in selected]
    log(f"Left for the next trip: {left}")
    dp_file = os.path.join(OUT_DIR, f"{name}_dp_table.csv")
    with open(dp_file, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["parcel\\capacity"] + list(range(capacity + 1)))
        w.writerow(["(none)"] + dp[0])
        for i, p in enumerate(ranked, 1):
            w.writerow([f"{p.pid} (w={p.weight},v={p.value})"] + dp[i])
    log(f"Full DP table saved to {os.path.relpath(dp_file)}")

    # ---------------- Phase 3a: Dijkstra ----------------
    log("\n--- PHASE 3a: Shortest paths (Dijkstra) ---")
    warehouse = 0
    stops = sorted({warehouse} | {p.dest for p in selected})
    D, prevs = distance_matrix(graph, stops)
    log(f"Stops to visit (node ids, 0 = warehouse): {stops}")
    log("Shortest distance from the warehouse to each stop:")
    for s in stops[1:]:
        path = build_path(prevs[warehouse], warehouse, s)
        arrow = " -> ".join(str(n) for n in path)
        log(f"  W -> {s:<3} {D[warehouse][s]:>7.1f} km   path: {arrow}")

    # ---------------- Phase 3b: nearest neighbour TSP ----------------
    log("\n--- PHASE 3b: Delivery route (Nearest-Neighbour TSP approximation) ---")
    tour = nearest_neighbor_tour(stops, D, warehouse)
    length = tour_length(tour, D)
    full = expand_tour(tour, prevs)
    log(f"Stop order   : {' -> '.join(('W' if s == warehouse else str(s)) for s in tour)}")
    log(f"Full road path: {' -> '.join(str(n) for n in full)}")
    log(f"Total route length: {length:.1f} km")
    if len(stops) - 1 <= 9:
        opt_tour, opt_len = brute_force_tour(stops, D, warehouse)
        log(f"Exact optimum (brute force over {len(stops) - 1} stops): {opt_len:.1f} km")
        log(f"Approximation ratio = {length / opt_len:.3f} (1.000 means optimal)")
    else:
        log("(Too many stops for brute force, optimum not computed.)")

    # ---------------- deadline check ----------------
    log("\n--- Deadline check (speed %.0f km/h, %.0f min per stop) ---" % (SPEED_KMH, SERVICE_MIN))
    clock_min, arrival = 0.0, {}
    for k, (a, b) in enumerate(zip(tour, tour[1:])):
        clock_min += D[a][b] / SPEED_KMH * 60
        if b != warehouse:
            arrival.setdefault(b, clock_min)
            clock_min += SERVICE_MIN
    late = 0
    for p in sorted(selected, key=lambda p: arrival[p.dest]):
        eta_h = arrival[p.dest] / 60
        ok = eta_h <= p.deadline_h
        late += not ok
        log(f"  {p.pid} -> node {p.dest:<3} arrives {eta_h:5.2f} h, deadline {p.deadline_h:>4} h  "
            f"{'OK' if ok else 'LATE'}")
    log(f"Parcels late: {late} of {len(selected)}   | trip finishes after {clock_min / 60:.2f} h")

    # ---------------- picture + log file ----------------
    img = os.path.join(OUT_DIR, f"{name}_route.png")
    plot_route(nodes, graph, full, tour,
               f"Delivery route ({name} dataset) - {length:.1f} km", img)
    log(f"\nRoute picture saved to {os.path.relpath(img)}")
    with open(os.path.join(OUT_DIR, f"{name}_run_log.txt"), "w") as f:
        f.write("\n".join(log.lines) + "\n")


if __name__ == "__main__":
    main()
