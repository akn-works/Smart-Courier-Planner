"""Data model for the Smart Courier Planner."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Parcel:
    pid: str          # parcel id, e.g. "P01"
    dest: int         # id of the graph node where the parcel must be delivered
    weight: int       # weight in kg (integer, needed by the knapsack DP table)
    value: int        # business value score (priority-weighted revenue)
    priority: int     # 1 = urgent, 2 = normal, 3 = low
    deadline_h: float # delivery deadline in hours from the start of the trip
