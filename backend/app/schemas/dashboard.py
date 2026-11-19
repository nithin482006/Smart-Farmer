from typing import Optional, List
from pydantic import BaseModel
from app.schemas.crops import CropGrowthStage
from app.schemas.weather import CurrentWeather, WeatherForecastDay
from app.schemas.risk import CropRiskAlert
from app.schemas.market import MarketPrice


class DashboardFarm(BaseModel):
    id: str
    name: str
    district: str
    state: Optional[str] = None
    land_area: Optional[float] = None
    area_unit: Optional[str] = "Acres"


class DashboardCrop(BaseModel):
    name: str
    variety: Optional[str] = None
    stage: CropGrowthStage
    sowing_date: Optional[str] = None


class DashboardResponse(BaseModel):
    farm: DashboardFarm
    weather: CurrentWeather
    crop: DashboardCrop
    risks: List[CropRiskAlert]
    market_prices: List[MarketPrice]
    upcoming_forecast: Optional[List[WeatherForecastDay]] = None
