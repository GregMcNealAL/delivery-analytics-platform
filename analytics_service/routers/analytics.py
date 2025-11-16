from fastapi import APIRouter, Depends, HTTPException
from analytics_service.schemas import AnalyticsSummary
from analytics_service.calculations import (
    average_delivery_time,
    average_cost,
    top_locations,
)
from analytics_service.core.config import settings
from analytics_service.core.http_client import get_http_client
import httpx

router = APIRouter()


@router.get("/summary", response_model=AnalyticsSummary)
async def get_analytics_summary(client: httpx.AsyncClient = Depends(get_http_client)):
    """
    Fetch orders from Orders Service, calculates stats, and return summary.
    """

    try:
        response = await client.get(f"{settings.ORDERS_API_URL}/orders")
        response.raise_for_status()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch orders: {e}")

    orders = response.json()

    return AnalyticsSummary(
        total_orders=len(orders),
        average_delivery_time=average_delivery_time(orders),
        average_cost=average_cost(orders),
        top_locations=top_locations(orders),
    )
