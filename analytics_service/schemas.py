from pydantic import BaseModel

class AnalyticsSummary(BaseModel):
    total_orders: int
    average_delivery_time: float
    average_cost: float
    top_locations: list[str]


class StatusBreakdown(BaseModel):
    statuses: dict[str, int]


class LocationCount(BaseModel):
    location: str
    count: int


class LocationBreakdown(BaseModel):
    top_locations: list[LocationCount]
