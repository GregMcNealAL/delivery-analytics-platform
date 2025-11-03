def average_delivery_time(orders: list[dict]) -> float:
    return sum(o["delivery_time"] for o in orders) / len(orders)

def average_cost(orders: list[dict]) -> float:
    return sum(o["cost"] for o in orders) / len(orders)

def top_locations(orders: list[dict], top_n=3) -> list[str]:
    from collections import Counter
    locations = [o["location"] for o in orders]
    return [loc for loc, _ in Counter(locations).most_common(top_n)]