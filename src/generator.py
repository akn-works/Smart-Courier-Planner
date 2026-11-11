"""Random dataset generator (used for the larger test datasets in Phase 4).

Usage:  python -m src.generator --prefix large --nodes 60 --parcels 40 --seed 7
"""
import argparse
import csv
import math
import os
import random

from .data_loader import DATA_DIR


def generate_graph(n_nodes, seed=1, area=20.0, k_near=3):
    """Random connected road network. Returns (coords, edges) where
    coords = {id: (x, y)} and edges = {(u, v): km} with u < v."""
    rnd = random.Random(seed)
    coords = {i: (round(rnd.uniform(0, area), 2), round(rnd.uniform(0, area), 2))
              for i in range(n_nodes)}

    def dist(a, b):
        return math.hypot(coords[a][0] - coords[b][0], coords[a][1] - coords[b][1])

    edges = {}

    def add(a, b):
        if a != b:
            edges[(min(a, b), max(a, b))] = round(dist(a, b) * 1.2, 1)  # 1.2 = road factor

    for a in range(n_nodes):                       # link each node to its nearest neighbours
        near = sorted((b for b in range(n_nodes) if b != a), key=lambda b: dist(a, b))
        for b in near[:k_near]:
            add(a, b)
    order = sorted(range(n_nodes), key=lambda i: coords[i][0])
    for a, b in zip(order, order[1:]):             # chain by x => guarantees connectivity
        add(a, b)
    return coords, edges


def generate_parcels(n_parcels, n_nodes, seed=1):
    rnd = random.Random(seed + 1000)
    parcels = []
    for i in range(1, n_parcels + 1):
        pr = rnd.choices([1, 2, 3], weights=[2, 4, 4])[0]
        deadline = {1: rnd.randint(2, 4), 2: rnd.randint(4, 8), 3: rnd.randint(8, 12)}[pr]
        value = {1: rnd.randint(60, 100), 2: rnd.randint(35, 70), 3: rnd.randint(15, 45)}[pr]
        parcels.append((f"P{i:03d}", rnd.randint(1, n_nodes - 1), rnd.randint(1, 15),
                        value, pr, deadline))
    return parcels


def write_dataset(prefix, n_nodes, n_parcels, seed):
    coords, edges = generate_graph(n_nodes, seed)
    parcels = generate_parcels(n_parcels, n_nodes, seed)
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(os.path.join(DATA_DIR, f"{prefix}_nodes.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "name", "x", "y"])
        for i, (x, y) in coords.items():
            w.writerow([i, "Warehouse" if i == 0 else f"Stop-{i}", x, y])
    with open(os.path.join(DATA_DIR, f"{prefix}_edges.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["u", "v", "km"])
        for (u, v), km in sorted(edges.items()):
            w.writerow([u, v, km])
    with open(os.path.join(DATA_DIR, f"{prefix}_parcels.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["pid", "dest", "weight", "value", "priority", "deadline_h"])
        w.writerows(parcels)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--prefix", default="large")
    ap.add_argument("--nodes", type=int, default=60)
    ap.add_argument("--parcels", type=int, default=40)
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()
    write_dataset(a.prefix, a.nodes, a.parcels, a.seed)
    print(f"Wrote datasets/{a.prefix}_[nodes|edges|parcels].csv")
