from typing import Optional, Literal
from pydantic import BaseModel, Field

AreaUnit = Literal["Acres", "Hectares", "Bigha", "Guntha"]


class FarmBase(BaseModel):
    name: str = Field(..., example="Green Valley Fields")
    state: str = Field(..., example="Karnataka")
    district: str = Field(..., example="Bengaluru Rural")
    village: Optional[str] = Field(None, example="Doddaballapura")
    latitude: float = Field(..., example=13.2984)
    longitude: float = Field(..., example=77.5358)
    land_area: float = Field(..., example=4.5)
    area_unit: AreaUnit = Field("Acres", example="Acres")
    is_primary: Optional[bool] = Field(False, example=True)


class FarmCreate(FarmBase):
    pass


class FarmResponse(FarmBase):
    id: str
    farmer_id: Optional[str] = None

    class Config:
        from_attributes = True
