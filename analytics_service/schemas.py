from pydantic import BaseModel

class AnalyticsSummary(BaseModel):
    total_orders: int
    average_delivery_time: float
    average_cost: float
    top_locations: list[str]