from pydantic import BaseModel
from typing import List

class AnalyticsSummary(BaseModel):
    total_orders: int
    average_delivery_time: float
    average_cost: float
    top_locations: List[str]