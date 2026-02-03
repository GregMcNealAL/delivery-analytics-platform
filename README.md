# Delivery Analytics Platform

This project is a two service FastAPI system with a tiny frontend that proves the data is flowing end to end. I built it to show clean service boundaries, reliable analytics calculations, and a simple UI that reads from a real API. It is intentionally compact, but the design mirrors how production systems separate data ownership from reporting.

**Highlights**
1. Two FastAPI services with a clear contract between them.
2. API key protection on both services plus rate limiting on analytics.
3. Analytics computed server side with retries and backoff for stability.
4. A single page frontend that fetches and renders live results.

**Architecture**
1. **orders_service** owns the order data and exposes CRUD endpoints.
2. **analytics_service** pulls orders from the orders service and computes summary metrics.
3. **index.html** calls the analytics summary endpoint and renders totals, averages, and top locations.

**Data flow**
1. Browser loads `index.html` from a local web server.
2. Frontend sends `GET /analytics/summary` with `X-API-Key`.
3. Analytics service calls `GET /orders` on the orders service using its own API key.
4. Analytics calculates totals, averages, and top locations, then returns the summary JSON.

**Tech stack**
1. FastAPI for both services.
2. PostgreSQL for persistence in the orders service.
3. httpx for async service to service requests.
4. Pydantic for request and response validation.
5. Plain HTML and modern ES6 JavaScript for the frontend.

**Key endpoints**
1. **Orders Service** `http://localhost:8000`
   - `GET /orders`
   - `GET /orders/{order_id}`
   - `POST /orders`
   - `PATCH /orders/{order_id}`
   - `DELETE /orders/{order_id}`
2. **Analytics Service** `http://localhost:8001`
   - `GET /analytics/summary`

**Response shape**
The analytics endpoint returns data like this:
```json
{
  "total_orders": 300,
  "average_delivery_time": 68.71,
  "average_cost": 250.63,
  "top_locations": [
    "Miami",
    "Springfield",
    "Los Angeles"
  ]
}
```

**Configuration**
Both services read an API key from `.env` and use it to authenticate requests between services.
```
ORDERS_API_KEY=dev-key
```
The orders service also reads from the project root `.env`:
```
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/ordersdb
```
The analytics service also reads:
```
ORDERS_API_URL=http://127.0.0.1:8000/orders
REQUEST_TIMEOUT=5.0
MAX_RETRIES=3
INITIAL_BACKOFF=0.5
```

**Run locally**
1. Set `ORDERS_API_KEY` and `DATABASE_URL` in the project root `.env`.
2. Start orders service:
   `uvicorn orders_service.main:app --reload --port 8000`
3. Start analytics service:
   `uvicorn analytics_service.main:app --reload --port 8001`
4. Serve the frontend from the project root:
   `python -m http.server 5500`
5. Open `http://localhost:5500/index.html`

**Why this structure**
The orders service stays focused on data storage and validation. The analytics service is free to evolve independently, add new calculations, or pull from other sources without touching the core data model. This split mirrors real systems where reporting workloads are isolated from transactional APIs.

**What I would add next**
1. Pagination and filtering on orders.
2. Aggregations grouped by time range.
3. A small test suite for analytics calculations and API auth.
4. A richer frontend with charts and trends.