import asyncio

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query

from analytics_service.rate_limiter import rate_limit_dependency
from analytics_service.core.config import settings
from analytics_service.core.http_client import get_http_client
from analytics_service.schemas import AnalyticsSummary, StatusBreakdown, LocationBreakdown
from analytics_service.calculations import (
    average_delivery_time,
    average_cost,
    top_locations,
    status_breakdown,
    top_locations_with_counts,
)

router = APIRouter(
    prefix="/analytics",
    tags=["analytics"],
    dependencies=[Depends(rate_limit_dependency)]
)


async def fetch_orders(client: httpx.AsyncClient) -> list[dict]:
    backoff = settings.INITIAL_BACKOFF

    for attempt in range(1, settings.MAX_RETRIES + 1):
        try:
            resp = await client.get(settings.ORDERS_API_URL, timeout=settings.REQUEST_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()

            if not isinstance(data, list):
                raise HTTPException(status_code=502, detail="Orders service returned invalid format")

            return data

        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 401:
                # auth failed dont retry
                raise HTTPException(status_code=502, detail="Orders service authentication failed")
            if attempt == settings.MAX_RETRIES:
                raise HTTPException(
                    status_code=502,
                    detail=f"Orders service returned status: {exc.response.status_code}"
                )

        except (httpx.RequestError, httpx.ConnectError) as exc:
            if attempt == settings.MAX_RETRIES:
                raise HTTPException(status_code=502, detail=f"Orders service network error: {exc}")

        await asyncio.sleep(backoff)
        backoff *= 2

    raise HTTPException(status_code=502, detail="Failed to fetch orders after retries")


@router.get("/summary", response_model=AnalyticsSummary)
async def get_summary(client: httpx.AsyncClient = Depends(get_http_client)):
    orders = await fetch_orders(client)

    total = len(orders)
    avg_delivery = average_delivery_time(orders) if orders else 0.0
    avg_cost_val = average_cost(orders) if orders else 0.0
    top_locs = top_locations(orders) if orders else []

    return AnalyticsSummary(
        total_orders=total,
        average_delivery_time=round(avg_delivery, 2),
        average_cost=round(avg_cost_val, 2),
        top_locations=top_locs,
    )


@router.get("/status-breakdown", response_model=StatusBreakdown)
async def get_status_breakdown(client: httpx.AsyncClient = Depends(get_http_client)):
    orders = await fetch_orders(client)
    return StatusBreakdown(statuses=status_breakdown(orders))


@router.get("/location-breakdown", response_model=LocationBreakdown)
async def get_location_breakdown(
    limit: int = Query(default=3, ge=1, le=50),
    client: httpx.AsyncClient = Depends(get_http_client),
):
    orders = await fetch_orders(client)
    return LocationBreakdown(top_locations=top_locations_with_counts(orders, top_n=limit))
