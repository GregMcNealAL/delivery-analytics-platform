from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from analytics_service.core.logging import setup_logging
from analytics_service.core.http_client import init_http_client, close_http_client
from analytics_service.routers.analytics import router as analytics_router

app = FastAPI(title="Analytics Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    setup_logging()
    await init_http_client()


@app.on_event("shutdown")
async def shutdown_event():
    await close_http_client()


app.include_router(analytics_router)
