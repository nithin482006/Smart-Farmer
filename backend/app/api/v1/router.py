from fastapi import APIRouter
from app.api.v1 import (
    health,
    farms,
    dashboard,
    crops,
    weather,
    risks,
    market,
    alerts,
)

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(farms.router)
api_router.include_router(dashboard.router)
api_router.include_router(crops.router)
api_router.include_router(weather.router)
api_router.include_router(risks.router)
api_router.include_router(market.router)
api_router.include_router(alerts.router)
