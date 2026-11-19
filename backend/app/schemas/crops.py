from typing import Optional, Literal
from pydantic import BaseModel, Field

CropGrowthStage = Literal[
    "Sowing",
    "Germination",
    "Vegetative",
    "Flowering",
    "Fruiting / Grain formation",
    "Maturity",
    "Harvesting",
]


class CropCycleCreate(BaseModel):
    farm_id: str
    crop_name: str
    variety: Optional[str] = None
    sowing_date: str
    current_stage: CropGrowthStage = "Flowering"


class CropCycleStageUpdate(BaseModel):
    stage: CropGrowthStage


class CropCycleResponse(BaseModel):
    id: str
    farm_id: str
    crop_name: str
    variety: Optional[str] = None
    sowing_date: str
    current_stage: CropGrowthStage
    target_harvest_date: Optional[str] = None
    expected_yield_tons: Optional[float] = None

    class Config:
        from_attributes = True
