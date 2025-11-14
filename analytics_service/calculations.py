from collections import Counter
from typing import List, Dict

def average_delivery_time(orders: List[Dict]) -> float:
    if not orders:
        return 0.0
    return sum(float(order.get("delivery_time", 0)) for order in orders) / len(orders)

def average_cost(orders: List[Dict]) -> float:
    if not orders:
        return 0.0 
    return sum(float(order.get("cost", 0)) for order in orders) / len(orders)

def top_locations(orders: List[Dict], top_n: int = 3) -> List[str]:
    locations = [order.get("location") for order in orders if order.get("location")]
    return [location for location, _ in Counter(locations).most_common(top_n)]