"""Sorting algorithms used to prioritise parcels (Phase 2).

Merge Sort is the algorithm used by the planner because:
  * worst-case O(n log n) (quick sort can degrade to O(n^2)),
  * it is STABLE - parcels with identical (priority, deadline) keep their input order,
  * the key can be a tuple, so we can sort by several criteria in one pass.
Insertion sort and quick sort are included only for the runtime comparison (Phase 4).
"""
import random


def merge_sort(items, key=lambda x: x):
    """Stable merge sort. Time O(n log n), extra space O(n)."""
    if len(items) <= 1:
        return list(items)
    mid = len(items) // 2
    left = merge_sort(items[:mid], key)
    right = merge_sort(items[mid:], key)
    return _merge(left, right, key)


def _merge(left, right, key):
    merged, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        # strict '<' for the right item => ties take from the left => stable
        if key(right[j]) < key(left[i]):
            merged.append(right[j])
            j += 1
        else:
            merged.append(left[i])
            i += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def insertion_sort(items, key=lambda x: x):
    """Simple O(n^2) sort - baseline for comparison."""
    a = list(items)
    for i in range(1, len(a)):
        cur, k = a[i], key(a[i])
        j = i - 1
        while j >= 0 and key(a[j]) > k:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = cur
    return a


def quick_sort(items, key=lambda x: x):
    """Randomised quick sort (average O(n log n), worst O(n^2), not stable)."""
    if len(items) <= 1:
        return list(items)
    pivot = key(items[random.randrange(len(items))])
    less = [x for x in items if key(x) < pivot]
    equal = [x for x in items if key(x) == pivot]
    more = [x for x in items if key(x) > pivot]
    return quick_sort(less, key) + equal + quick_sort(more, key)
