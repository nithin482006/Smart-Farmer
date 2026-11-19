from fastapi import APIRouter, Depends, status
from app.core.auth import get_current_user
from app.schemas.crops import CropCycleCreate, CropCycleStageUpdate, CropCycleResponse
from app.services.farmer_data import FarmerDataService

router = APIRouter(prefix="/crop-cycles", tags=["Crops"])


@router.post("", response_model=CropCycleResponse, status_code=status.HTTP_201_CREATED)
def create_crop_cycle(cycle: CropCycleCreate, user: dict = Depends(get_current_user)):
    """
    Registers a new crop on a farm parcel.
    """
    return FarmerDataService.create_crop_cycle(cycle)


@router.patch("/{cycle_id}/stage")
def update_crop_stage(cycle_id: str, payload: CropCycleStageUpdate, user: dict = Depends(get_current_user)):
    """
    Updates the crop's phenological stage.
    """
    FarmerDataService.update_crop_stage(cycle_id, payload.stage)
    return {"success": True, "stage": payload.stage}
