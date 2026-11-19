from typing import Optional, Literal
from pydantic import BaseModel, Field


class MarketPrice(BaseModel):
    id: str
    commodity: str = Field(..., example="Paddy (Dhan) - Common")
    state: str = Field(..., example="Karnataka")
    district: str = Field(..., example="Bengaluru Rural")
    mandi_name: str = Field(..., example="Doddaballapura APMC")
    min_price: float = Field(..., example=2180)
    max_price: float = Field(..., example=2350)
    modal_price: float = Field(..., example=2280)
    unit: str = Field("Quintal", example="Quintal")
    reporting_date: str = Field(..., example="2026-11-18")
    trend: Optional[Literal["up", "down", "stable"]] = "up"
    change_percentage: Optional[float] = 2.4
