"""Reads the CSV datasets (nodes, edges, parcels) from the datasets/ folder."""
import csv
import os

from .models import Parcel

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "datasets")
OUT_DIR = os.path.join(ROOT, "outputs")


def _path(prefix, kind):
    return os.path.join(DATA_DIR, f"{prefix}_{kind}.csv")


def load_nodes(prefix):
    """Returns {node_id: (name, x, y)}."""
    nodes = {}
    with open(_path(prefix, "nodes"), newline="") as f:
        for row in csv.DictReader(f):
            nodes[int(row["id"])] = (row["name"], float(row["x"]), float(row["y"]))
    return nodes


def load_edges(prefix):
    """Returns an undirected adjacency list {u: [(v, km), ...]}."""
    graph = {}
    with open(_path(prefix, "edges"), newline="") as f:
        for row in csv.DictReader(f):
            u, v, w = int(row["u"]), int(row["v"]), float(row["km"])
            graph.setdefault(u, []).append((v, w))
            graph.setdefault(v, []).append((u, w))
    return graph


def load_parcels(prefix):
    parcels = []
    with open(_path(prefix, "parcels"), newline="") as f:
        for row in csv.DictReader(f):
            parcels.append(Parcel(
                pid=row["pid"], dest=int(row["dest"]), weight=int(row["weight"]),
                value=int(row["value"]), priority=int(row["priority"]),
                deadline_h=float(row["deadline_h"]),
            ))
    return parcels
