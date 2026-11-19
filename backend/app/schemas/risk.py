from typing import Optional, Literal
from pydantic import BaseModel, Field
from app.schemas.crops import CropGrowthStage

RiskSeverity = Literal["low", "moderate", "high", "critical"]


class CropRiskAlert(BaseModel):
    id: str
    farm_id: Optional[str] = None
    crop_name: str = Field(..., example="Paddy (Rice)")
    crop_stage: CropGrowthStage = Field("Flowering", example="Flowering")
    hazard: str = Field(..., example="Heavy Rainfall & Pollen Washout Warning")
    severity: RiskSeverity = Field("high", example="high")
    reason: str = Field(..., example="Forecast rainfall of 14-22mm coincides with active flowering. Rain wash-out prevents pollination.")
    advisory: str = Field(..., example="Ensure drainage channels in paddy basins are clear. Postpone urea top-dressing and chemical sprays.")
    forecast_period: Optional[str] = Field("Next 24 to 48 Hours", example="Next 24 to 48 Hours")
    source: str = Field("IMD Agromet Advisory Service", example="IMD Agromet Advisory Service")
    timestamp: str = Field(..., example="2026-11-19T08:30:00Z")
    is_read: Optional[bool] = False
