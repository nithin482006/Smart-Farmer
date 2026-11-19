from fastapi import APIRouter, HTTPException
from app.database import supabase
from app.models.schemas import MarketPriceCreate

router = APIRouter()


@router.post("/prices")
async def add_market_price(price: MarketPriceCreate):
    try:
        response = (
            supabase.table("market_prices")
            .insert(price.model_dump())
            .execute()
        )
        return {"message": "Market price recorded", "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/prices")
async def get_all_prices():
    try:
        response = (
            supabase.table("market_prices")
            .select("*")
            .order("recorded_at", desc=True)
            .execute()
        )
        return {"data": response.data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/prices/{crop_name}")
async def get_prices_by_crop(crop_name: str):
    try:
        response = (
            supabase.table("market_prices")
            .select("*")
            .ilike("crop_name", f"%{crop_name}%")
            .order("recorded_at", desc=True)
            .execute()
        )
        return {"data": response.data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/prices/location/{location}")
async def get_prices_by_location(location: str):
    try:
        response = (
            supabase.table("market_prices")
            .select("*")
            .ilike("location", f"%{location}%")
            .order("recorded_at", desc=True)
            .execute()
        )
        return {"data": response.data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
