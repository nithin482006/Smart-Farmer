from fastapi import APIRouter, HTTPException
from app.database import supabase
from app.models.schemas import CropCreate, CropUpdate

router = APIRouter()


@router.post("/")
async def add_crop(crop: CropCreate):
    try:
        response = (
            supabase.table("crops")
            .insert(crop.model_dump())
            .execute()
        )
        return {"message": "Crop added", "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/")
async def get_all_crops():
    try:
        response = supabase.table("crops").select("*").execute()
        return {"data": response.data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/farmer/{farmer_id}")
async def get_crops_by_farmer(farmer_id: str):
    try:
        response = (
            supabase.table("crops")
            .select("*")
            .eq("farmer_id", farmer_id)
            .execute()
        )
        return {"data": response.data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{crop_id}")
async def get_crop(crop_id: str):
    try:
        response = (
            supabase.table("crops")
            .select("*")
            .eq("id", crop_id)
            .single()
            .execute()
        )
        return {"data": response.data}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{crop_id}")
async def update_crop(crop_id: str, crop: CropUpdate):
    try:
        response = (
            supabase.table("crops")
            .update(crop.model_dump(exclude_unset=True))
            .eq("id", crop_id)
            .execute()
        )
        return {"message": "Crop updated", "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{crop_id}")
async def delete_crop(crop_id: str):
    try:
        supabase.table("crops").delete().eq("id", crop_id).execute()
        return {"message": "Crop deleted"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
