from typing import List
from fastapi import APIRouter, Depends
from app.core.auth import get_current_user
from app.schemas.risk import CropRiskAlert
from app.services.farmer_data import FarmerDataService

router = APIRouter(prefix="/risks", tags=["Risks"])


@router.get("/{farm_id}", response_model=List[CropRiskAlert])
def get_risks(farm_id: str, user: dict = Depends(get_current_user)):
    """
    Returns active risk alerts and advisories for the farm's active crops.
    """
    return FarmerDataService.get_risks(farm_id)
