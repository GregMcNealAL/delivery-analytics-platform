# Delivery Analytics Platform

This project is a small multi-service backend system with a Go API gateway, two FastAPI services, and a simple frontend. It demonstrates service boundaries, authenticated service-to-service calls, retry/backoff behavior, and tested routing/auth contracts.

**Highlights**
1. Go gateway routes `/orders` and `/analytics` to separate upstream services.
2. API key protection at gateway, orders service, and analytics service.
3. Analytics service computes multiple views: summary, status breakdown, and location breakdown.
4. Retry/backoff logic for upstream orders calls in analytics.
5. Automated tests for gateway routing/auth, analytics retry behavior, and cross-service integration.

**Architecture**
1. **gateway** (Go) receives client requests on `:8080`, validates `X-API-Key`, and proxies to upstream services.
2. **orders_service** (FastAPI) owns order data and exposes CRUD endpoints backed by PostgreSQL.
3. **analytics_service** (FastAPI) fetches orders from `orders_service` and computes analytics responses.
4. **index.html** calls the gateway endpoint and renders analytics data.

**Data flow**
1. Browser loads `index.html` from a local web server.
2. Frontend sends `GET /analytics/summary` with `X-API-Key` to the gateway on `:8080`.
3. Gateway validates the API key and proxies `/analytics/*` requests to `analytics_service`.
4. Analytics service validates API key + rate limit, then calls `GET /orders` on `orders_service` via `httpx`.
5. Orders service validates API key, returns order data from PostgreSQL, and analytics computes the response.

**Tech stack**
1. Go standard library (`net/http`, `httputil`) for the gateway.
2. FastAPI for `orders_service` and `analytics_service`.
3. PostgreSQL + SQLAlchemy for order persistence.
4. httpx for async service-to-service requests.
5. Pydantic for request/response validation.
6. pytest and Go `testing` for automated tests.
7. Plain HTML and ES6 JavaScript for the frontend.

**Key endpoints**
1. **Gateway** `http://localhost:8080`
   - `GET|POST|PATCH|DELETE /orders...` (proxied to orders service)
   - `GET /analytics/summary`
   - `GET /analytics/status-breakdown`
   - `GET /analytics/location-breakdown?limit=3`
2. **Orders Service** `http://localhost:8000`
   - `GET /orders`
   - `GET /orders/{order_id}`
   - `POST /orders`
   - `PATCH /orders/{order_id}`
   - `DELETE /orders/{order_id}`
3. **Analytics Service** `http://localhost:8001`
   - `GET /analytics/summary`
   - `GET /analytics/status-breakdown`
   - `GET /analytics/location-breakdown?limit=3`

**Response shape**
The analytics summary endpoint returns data like this:
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
The status breakdown endpoint returns data like this:
```json
{
  "statuses": {
    "delivered": 120,
    "pending": 100,
    "cancelled": 80
  }
}
```
The location breakdown endpoint returns data like this:
```json
{
  "top_locations": [
    { "location": "Miami", "count": 42 },
    { "location": "Springfield", "count": 35 },
    { "location": "Los Angeles", "count": 31 }
  ]
}
```

**Configuration**
Python services read configuration from the project root `.env`. The Go gateway reads process environment variables (`os.Getenv`), so those values must be present in the gateway process environment.
```
ORDERS_API_KEY=dev-key
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/ordersdb
ORDERS_UPSTREAM_URL=http://localhost:8000
ANALYTICS_UPSTREAM_URL=http://localhost:8001
ORDERS_API_URL=http://127.0.0.1:8000/orders
REQUEST_TIMEOUT=5.0
MAX_RETRIES=3
INITIAL_BACKOFF=0.5
```

**Run locally**
1. Set Python service values in the project root `.env` (`ORDERS_API_KEY`, `DATABASE_URL`, retry config). Export/set gateway env vars in your shell (`ORDERS_API_KEY`, `ORDERS_UPSTREAM_URL`, `ANALYTICS_UPSTREAM_URL`) before running the gateway.
2. Start orders service:
   `uvicorn orders_service.main:app --reload --port 8000`
3. Start analytics service:
   `uvicorn analytics_service.main:app --reload --port 8001`
4. Start gateway:
   `go run gateway/main.go`
5. Serve the frontend from the project root:
   `python -m http.server 5500`
6. Open `http://localhost:5500/index.html`

**Testing**
1. Run Python tests:
   `.\venv\Scripts\python.exe -m pytest -q`
2. Run gateway tests:
   `cd gateway && go test ./...`

**Why this structure**
Orders stays focused on transactional data storage and validation. Analytics stays focused on read-side aggregation and reporting logic. The gateway centralizes external routing/auth behavior. This separation mirrors common backend architecture where each service has a narrow responsibility and explicit contract.

**What I would add next**
1. Pagination and filtering on orders endpoints.
2. Time-window analytics and trend endpoints.
3. Persistent/distributed rate limiting for multi-instance deployments.
4. CI pipeline (pytest + go test) with coverage reporting.
