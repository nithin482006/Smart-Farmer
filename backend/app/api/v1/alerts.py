from typing import List
from fastapi import APIRouter, Depends
from app.core.auth import get_current_user
from app.schemas.risk import CropRiskAlert
from app.services.farmer_data import FarmerDataService

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("", response_model=List[CropRiskAlert])
def get_alerts(user: dict = Depends(get_current_user)):
    """
    Returns warning and risk alerts for the authenticated farmer.
    """
    return FarmerDataService.get_alerts()


@router.patch("/{alert_id}/read")
def mark_alert_read(alert_id: str, user: dict = Depends(get_current_user)):
    """
    Marks an alert as read / acknowledged.
    """
    FarmerDataService.mark_alert_read(alert_id)
    return {"success": True, "alert_id": alert_id}
