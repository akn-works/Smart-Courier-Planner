"""Correctness tests (Phase 4 evidence). Run:  python -m unittest discover -s tests -v"""
import os
import random
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.generator import generate_graph
from src.graph_routing import (brute_force_tour, build_path, dijkstra, distance_matrix,
                               nearest_neighbor_tour, tour_length)
from src.knapsack import knapsack_01, knapsack_bruteforce
from src.sorting import insertion_sort, merge_sort, quick_sort


class SortingTests(unittest.TestCase):
    def test_matches_python_sorted(self):
        rnd = random.Random(1)
        for n in [0, 1, 2, 10, 100, 500]:
            data = [rnd.randint(-50, 50) for _ in range(n)]
            self.assertEqual(merge_sort(data), sorted(data))
            self.assertEqual(insertion_sort(data), sorted(data))
            self.assertEqual(quick_sort(data), sorted(data))

    def test_merge_sort_is_stable(self):
        data = [("a", 2), ("b", 1), ("c", 2), ("d", 1), ("e", 2)]
        self.assertEqual([x[0] for x in merge_sort(data, key=lambda t: t[1])],
                         ["b", "d", "a", "c", "e"])

    def test_tuple_key_priority_then_deadline(self):
        parcels = [(2, 5), (1, 9), (1, 3), (2, 1)]
        self.assertEqual(merge_sort(parcels), [(1, 3), (1, 9), (2, 1), (2, 5)])


class KnapsackTests(unittest.TestCase):
    def test_textbook_example(self):
        best, chosen, _ = knapsack_01([1, 3, 4, 5], [1, 4, 5, 7], 7)
        self.assertEqual(best, 9)           # items with weight 3 and 4
        self.assertEqual(sorted(chosen), [1, 2])

    def test_against_brute_force(self):
        rnd = random.Random(5)
        for _ in range(60):
            n = rnd.randint(1, 10)
            w = [rnd.randint(1, 9) for _ in range(n)]
            v = [rnd.randint(1, 50) for _ in range(n)]
            cap = rnd.randint(1, 30)
            best, chosen, _ = knapsack_01(w, v, cap)
            self.assertEqual(best, knapsack_bruteforce(w, v, cap))
            self.assertLessEqual(sum(w[i] for i in chosen), cap)
            self.assertEqual(sum(v[i] for i in chosen), best)

    def test_nothing_fits(self):
        self.assertEqual(knapsack_01([10, 20], [5, 5], 3)[0], 0)


class GraphTests(unittest.TestCase):
    def setUp(self):
        # 0 -1- 1 -1- 2 ; 0 -5- 2 ; 2 -2- 3   => shortest 0->2 is 2 (via 1)
        self.g = {0: [(1, 1), (2, 5)], 1: [(0, 1), (2, 1)],
                  2: [(1, 1), (0, 5), (3, 2)], 3: [(2, 2)]}

    def test_dijkstra_distances_and_path(self):
        dist, prev = dijkstra(self.g, 0)
        self.assertEqual(dist, {0: 0, 1: 1, 2: 2, 3: 4})
        self.assertEqual(build_path(prev, 0, 3), [0, 1, 2, 3])

    def test_disconnected_node_is_infinite(self):
        g = {0: [(1, 1)], 1: [(0, 1)], 2: []}
        dist, prev = dijkstra(g, 0)
        self.assertEqual(dist[2], float("inf"))
        self.assertEqual(build_path(prev, 0, 2), [])

    def test_tour_is_valid_and_not_better_than_optimum(self):
        coords, edges = generate_graph(30, seed=3)
        adj = {i: [] for i in range(30)}
        for (u, v), w in edges.items():
            adj[u].append((v, w))
            adj[v].append((u, w))
        stops = [0, 4, 9, 13, 21, 27]
        D, _ = distance_matrix(adj, stops)
        tour = nearest_neighbor_tour(stops, D, 0)
        self.assertEqual(tour[0], 0)
        self.assertEqual(tour[-1], 0)
        self.assertEqual(sorted(tour[:-1]), sorted(stops))     # every stop exactly once
        _, opt = brute_force_tour(stops, D, 0)
        self.assertGreaterEqual(tour_length(tour, D) + 1e-9, opt)


if __name__ == "__main__":
    unittest.main()
