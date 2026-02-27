from collections import Counter

def average_delivery_time(orders: list[dict]) -> float:
    if not orders:
        return 0.0
    return sum(float(order.get("delivery_time", 0)) for order in orders) / len(orders)

def average_cost(orders: list[dict]) -> float:
    if not orders:
        return 0.0 
    return sum(float(order.get("cost", 0)) for order in orders) / len(orders)

def top_locations(orders: list[dict], top_n: int = 3) -> list[str]:
    locations = [order.get("location") for order in orders if order.get("location")]
    return [location for location, _ in Counter(locations).most_common(top_n)]


def status_breakdown(orders: list[dict]) -> dict[str, int]:
    statuses = [str(order.get("status")) for order in orders if order.get("status")]
    return dict(Counter(statuses))


def top_locations_with_counts(orders: list[dict], top_n: int = 3) -> list[dict]:
    locations = [order.get("location") for order in orders if order.get("location")]
    return [
        {"location": location, "count": count}
        for location, count in Counter(locations).most_common(top_n)
    ]
