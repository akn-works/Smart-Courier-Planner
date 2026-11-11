"""0/1 Knapsack by Dynamic Programming (Phase 2).

dp[i][c] = best total value using only the first i parcels with a van capacity of c kg.
Recurrence:  dp[i][c] = dp[i-1][c]                                       (skip parcel i)
             dp[i][c] = max(dp[i][c], dp[i-1][c-w_i] + v_i)  if w_i <= c  (take parcel i)
Time O(n*C), space O(n*C) (the full table is kept so we can print it and back-track).
"""
from itertools import combinations


def knapsack_01(weights, values, capacity):
    """Returns (best_value, chosen_indices, dp_table)."""
    n = len(weights)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        w, v = weights[i - 1], values[i - 1]
        for c in range(capacity + 1):
            dp[i][c] = dp[i - 1][c]
            if w <= c and dp[i - 1][c - w] + v > dp[i][c]:
                dp[i][c] = dp[i - 1][c - w] + v
    # back-track: if the value changed between row i-1 and row i, parcel i was taken
    chosen, c = [], capacity
    for i in range(n, 0, -1):
        if dp[i][c] != dp[i - 1][c]:
            chosen.append(i - 1)
            c -= weights[i - 1]
    chosen.reverse()
    return dp[n][capacity], chosen, dp


def greedy_fill(weights, values, capacity):
    """Takes parcels in the given (already sorted) order while they fit. Used only to
    show that greedy filling is NOT optimal compared with DP."""
    total_w = total_v = 0
    chosen = []
    for i, (w, v) in enumerate(zip(weights, values)):
        if total_w + w <= capacity:
            total_w += w
            total_v += v
            chosen.append(i)
    return total_v, chosen


def knapsack_bruteforce(weights, values, capacity):
    """Checks all 2^n subsets - only for unit tests on tiny inputs."""
    n, best = len(weights), 0
    for r in range(n + 1):
        for combo in combinations(range(n), r):
            if sum(weights[i] for i in combo) <= capacity:
                best = max(best, sum(values[i] for i in combo))
    return best
