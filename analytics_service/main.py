from fastapi import FastAPI
import requests

from analytics_service.schemas import AnalyticsSummary
from analytics_service.calculations import average_delivery_time, average_cost, top_locations

app = FastAPI(title="Analytics Service")

ORDERS_API_URL = "http://127.0.0.1:8000/orders"

@app.get("/analytics/summary", response_model=AnalyticsSummary)
def get_summary():
    response = requests.get(ORDERS_API_URL)
    orders = response.json()

    summary = AnalyticsSummary(
        total_orders=len(orders),
        average_delivery_time=average_delivery_time(orders),
        average_cost=average_cost(orders),
        top_locations=top_locations(orders)
    )

    return summary
