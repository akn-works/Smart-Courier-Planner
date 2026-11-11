"""Graph algorithms (Phase 3): Dijkstra + nearest-neighbour TSP approximation."""
import heapq
import itertools
import math


def dijkstra(graph, source):
    """Single-source shortest paths with a binary heap. O((V+E) log V).
    Returns (dist, prev)."""
    dist = {u: math.inf for u in graph}
    prev = {u: None for u in graph}
    dist[source] = 0.0
    heap = [(0.0, source)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:           # stale heap entry
            continue
        for v, w in graph[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                prev[v] = u
                heapq.heappush(heap, (nd, v))
    return dist, prev


def build_path(prev, source, target):
    """Rebuilds the node sequence source -> target from the predecessor map."""
    path, u = [], target
    while u is not None:
        path.append(u)
        u = prev[u]
    path.reverse()
    return path if path and path[0] == source else []


def distance_matrix(graph, stops):
    """Runs Dijkstra from every stop. Returns (D, prevs) where D[a][b] = shortest km."""
    D, prevs = {}, {}
    for s in stops:
        dist, prev = dijkstra(graph, s)
        D[s] = {t: dist[t] for t in stops}
        prevs[s] = prev
    return D, prevs


def nearest_neighbor_tour(stops, D, start):
    """Greedy TSP approximation: always drive to the closest unvisited stop,
    then return to the start. O(k^2) for k stops. Not optimal, but fast."""
    unvisited = set(stops) - {start}
    tour, cur = [start], start
    while unvisited:
        nxt = min(unvisited, key=lambda s: (D[cur][s], s))   # tie-break by id
        if D[cur][nxt] == math.inf:
            raise ValueError(f"stop {nxt} is unreachable from {cur}")
        tour.append(nxt)
        unvisited.remove(nxt)
        cur = nxt
    tour.append(start)
    return tour


def tour_length(tour, D):
    return sum(D[a][b] for a, b in zip(tour, tour[1:]))


def brute_force_tour(stops, D, start):
    """Exact TSP by trying every order - only feasible for <= 9 customer stops.
    Used to measure how good the nearest-neighbour answer is."""
    others = [s for s in stops if s != start]
    best_tour, best_len = None, math.inf
    for perm in itertools.permutations(others):
        t = [start, *perm, start]
        L = tour_length(t, D)
        if L < best_len:
            best_tour, best_len = t, L
    return best_tour, best_len


def expand_tour(tour, prevs):
    """Turns a tour over stops into the full list of road nodes driven."""
    full = [tour[0]]
    for a, b in zip(tour, tour[1:]):
        seg = build_path(prevs[a], a, b)
        full.extend(seg[1:])
    return full
