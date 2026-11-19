from typing import Optional, List, Literal
from pydantic import BaseModel, Field

RiskSeverity = Literal["low", "moderate", "high", "critical"]


class CurrentWeather(BaseModel):
    temperature_c: float = Field(..., example=26)
    temp_min_c: Optional[float] = Field(None, example=19)
    temp_max_c: Optional[float] = Field(None, example=29)
    humidity: float = Field(..., example=75)
    rainfall_mm: float = Field(..., example=14)
    wind_speed_kmh: Optional[float] = Field(None, example=12)
    condition: str = Field(..., example="Thunderstorms / Overcast")
    rain_probability: Optional[float] = Field(None, example=75)
    source: str = Field("IMD (India Meteorological Department)", example="IMD")
    updated_at: str = Field(..., example="2026-11-19T10:00:00Z")


class WeatherForecastDay(BaseModel):
    date: str
    day_name: str
    temp_max_c: float
    temp_min_c: float
    rainfall_probability: float
    rainfall_expected_mm: float
    condition: str
    risk_level: RiskSeverity = "moderate"


class HistoricalWeatherPoint(BaseModel):
    date: str
    rainfall_mm: float
    temp_avg_c: float
    humidity_avg: float


class WeatherResponse(BaseModel):
    current: CurrentWeather
    forecast: List[WeatherForecastDay]
    historical: List[HistoricalWeatherPoint]
