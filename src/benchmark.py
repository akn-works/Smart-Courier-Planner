"""Phase 4 - runtime measurements, quality check and charts.

    python -m src.benchmark
Writes outputs/runtime_results.csv, outputs/runtime_chart.png, outputs/quality_chart.png
"""
import csv
import os
import random
import statistics
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .data_loader import OUT_DIR
from .generator import generate_graph
from .graph_routing import (brute_force_tour, dijkstra, distance_matrix,
                            nearest_neighbor_tour, tour_length)
from .knapsack import knapsack_01
from .sorting import insertion_sort, merge_sort, quick_sort


def timed(fn, repeats=3):
    """Median wall-clock seconds over several repeats (median ignores one-off spikes)."""
    runs = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        fn()
        runs.append(time.perf_counter() - t0)
    return statistics.median(runs)


def to_adj(n, edges):
    adj = {i: [] for i in range(n)}
    for (u, v), w in edges.items():
        adj[u].append((v, w))
        adj[v].append((u, w))
    return adj


def bench_sorting(rows):
    sizes = [100, 250, 500, 1000, 2000, 4000]
    for n in sizes:
        rnd = random.Random(n)
        data = [(rnd.randint(1, 3), rnd.randint(1, 12), -rnd.randint(10, 100)) for _ in range(n)]
        for label, fn in [("merge_sort", merge_sort), ("quick_sort", quick_sort),
                          ("insertion_sort", insertion_sort), ("python_sorted", None)]:
            if fn is None:
                t = timed(lambda: sorted(data))
            else:
                t = timed(lambda: fn(data))
            rows.append(("sorting", label, n, t))
        print(f"  sorting n={n} done")


def bench_knapsack(rows):
    for n in [10, 25, 50, 100, 200, 400]:
        rnd = random.Random(n)
        w = [rnd.randint(1, 15) for _ in range(n)]
        v = [rnd.randint(10, 100) for _ in range(n)]
        t = timed(lambda: knapsack_01(w, v, 500), repeats=3)
        rows.append(("knapsack_dp (C=500)", "knapsack_01", n, t))
        print(f"  knapsack n={n} done")


def bench_dijkstra(rows):
    for n in [50, 100, 200, 500, 1000, 2000]:
        coords, edges = generate_graph(n, seed=n)
        adj = to_adj(n, edges)
        t = timed(lambda: dijkstra(adj, 0))
        rows.append(("dijkstra (one source)", "dijkstra", n, t))
        print(f"  dijkstra V={n} done")


def bench_tsp(rows):
    n_nodes = 500
    coords, edges = generate_graph(n_nodes, seed=99)
    adj = to_adj(n_nodes, edges)
    for k in [10, 25, 50, 100, 200, 400]:
        stops = list(range(k + 1))
        D, _ = distance_matrix(adj, stops)
        t = timed(lambda: nearest_neighbor_tour(stops, D, 0))
        rows.append(("nearest_neighbour_tsp", "nn_tsp", k, t))
        print(f"  nn tsp k={k} done")


def bench_quality():
    """How far is nearest-neighbour from the true optimum? (needs small k)"""
    n_nodes = 40
    results = []
    for k in range(4, 10):
        ratios = []
        for seed in range(15):
            coords, edges = generate_graph(n_nodes, seed=seed)
            adj = to_adj(n_nodes, edges)
            rnd = random.Random(seed * 31 + k)
            stops = [0] + rnd.sample(range(1, n_nodes), k)
            D, _ = distance_matrix(adj, stops)
            nn = tour_length(nearest_neighbor_tour(stops, D, 0), D)
            _, opt = brute_force_tour(stops, D, 0)
            ratios.append(nn / opt)
        results.append((k, statistics.mean(ratios), max(ratios)))
        print(f"  quality k={k} done")
    return results


def plot_runtime(rows, path):
    groups = {}
    for g, label, n, t in rows:
        groups.setdefault(g, {}).setdefault(label, []).append((n, t))
    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    titles = [("sorting", "Sorting parcels: runtime vs n", "number of parcels n"),
              ("knapsack_dp (C=500)", "0/1 Knapsack DP: runtime vs n  (O(nC))", "number of parcels n"),
              ("dijkstra (one source)", "Dijkstra: runtime vs V  (O((V+E) log V))", "number of road nodes V"),
              ("nearest_neighbour_tsp", "Nearest-neighbour TSP: runtime vs k  (O(k^2))", "number of stops k")]
    for ax, (g, title, xlabel) in zip(axes.flat, titles):
        for label, pts in groups[g].items():
            ax.plot([p[0] for p in pts], [p[1] * 1000 for p in pts], marker="o", label=label)
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel("time (ms)" + (", log scale" if g == "sorting" else ""))
        if g == "sorting":
            ax.set_yscale("log")   # insertion sort is so slow it would flatten the others
        ax.grid(alpha=0.3)
        ax.legend()
    fig.suptitle("Smart Courier Planner - measured runtime of the major steps")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_quality(results, path):
    ks = [r[0] for r in results]
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(ks, [r[1] for r in results], marker="o", label="average NN / optimum")
    ax.plot(ks, [r[2] for r in results], marker="s", label="worst NN / optimum")
    ax.axhline(1.0, color="green", linestyle="--", label="optimal (ratio 1.0)")
    ax.set_xlabel("number of delivery stops k")
    ax.set_ylabel("route length ratio")
    ax.set_title("Quality of nearest-neighbour TSP (15 random networks per k)")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    rows = []
    print("Benchmarking (takes about a minute)...")
    bench_sorting(rows)
    bench_knapsack(rows)
    bench_dijkstra(rows)
    bench_tsp(rows)
    quality = bench_quality()

    with open(os.path.join(OUT_DIR, "runtime_results.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["step", "algorithm", "input_size", "seconds"])
        for r in rows:
            w.writerow([r[0], r[1], r[2], f"{r[3]:.6f}"])
    with open(os.path.join(OUT_DIR, "quality_results.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["stops_k", "avg_ratio", "worst_ratio"])
        for k, a, m in quality:
            w.writerow([k, f"{a:.4f}", f"{m:.4f}"])
    plot_runtime(rows, os.path.join(OUT_DIR, "runtime_chart.png"))
    plot_quality(quality, os.path.join(OUT_DIR, "quality_chart.png"))

    print("\nRuntime table (ms):")
    for r in rows:
        print(f"  {r[0]:<26}{r[1]:<16}n={r[2]:<5}{r[3] * 1000:>10.3f} ms")
    print("\nNN-TSP quality:")
    for k, a, m in quality:
        print(f"  k={k}: average ratio {a:.3f}, worst {m:.3f}")
    print("\nSaved charts + CSVs to outputs/")


if __name__ == "__main__":
    main()
