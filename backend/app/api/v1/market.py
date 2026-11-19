from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from app.core.auth import get_current_user
from app.schemas.market import MarketPrice
from app.services.farmer_data import FarmerDataService

router = APIRouter(prefix="/market", tags=["Market"])


@router.get("/prices", response_model=List[MarketPrice])
def get_market_prices(
    commodity: Optional[str] = Query(None, description="Crop / commodity name"),
    district: Optional[str] = Query(None, description="District name"),
    user: dict = Depends(get_current_user),
):
    """
    Returns latest APMC mandi commodity prices matching commodity and/or district.
    """
    return FarmerDataService.get_market_prices(commodity=commodity, district=district)
