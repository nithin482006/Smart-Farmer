from fastapi import APIRouter, Depends
from app.core.auth import get_current_user
from app.schemas.dashboard import DashboardResponse
from app.services.farmer_data import FarmerDataService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/{farm_id}", response_model=DashboardResponse)
def get_dashboard(farm_id: str, user: dict = Depends(get_current_user)):
    """
    Returns aggregated data for the main farmer dashboard for a specific farm.
    """
    return FarmerDataService.get_dashboard(farm_id)
