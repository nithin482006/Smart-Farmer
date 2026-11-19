from typing import List
from fastapi import APIRouter, Depends, status
from app.core.auth import get_current_user
from app.schemas.farm import FarmResponse, FarmCreate
from app.services.farmer_data import FarmerDataService

router = APIRouter(prefix="/farms", tags=["Farms"])


@router.get("", response_model=List[FarmResponse])
def get_farms(user: dict = Depends(get_current_user)):
    """
    Returns all farms belonging to the authenticated farmer.
    """
    return FarmerDataService.get_farms(user["id"])


@router.post("", response_model=FarmResponse, status_code=status.HTTP_201_CREATED)
def create_farm(farm: FarmCreate, user: dict = Depends(get_current_user)):
    """
    Creates a new farm parcel for the authenticated farmer.
    """
    return FarmerDataService.create_farm(farm, user["id"])
