from fastapi import APIRouter, Depends
from app.core.auth import get_current_user
from app.schemas.weather import WeatherResponse
from app.services.farmer_data import FarmerDataService

router = APIRouter(prefix="/weather", tags=["Weather"])


@router.get("/{farm_id}", response_model=WeatherResponse)
def get_weather(farm_id: str, user: dict = Depends(get_current_user)):
    """
    Returns current weather observations, upcoming 5-day forecasts, and historical trends.
    """
    return FarmerDataService.get_weather(farm_id)
