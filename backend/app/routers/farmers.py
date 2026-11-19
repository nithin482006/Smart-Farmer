from fastapi import APIRouter, HTTPException
from app.database import supabase
from app.models.schemas import FarmerCreate, FarmerUpdate

router = APIRouter()


@router.post("/")
async def create_farmer(farmer: FarmerCreate):
    try:
        response = (
            supabase.table("farmers")
            .insert(farmer.model_dump())
            .execute()
        )
        return {"message": "Farmer profile created", "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/")
async def get_all_farmers():
    try:
        response = supabase.table("farmers").select("*").execute()
        return {"data": response.data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{farmer_id}")
async def get_farmer(farmer_id: str):
    try:
        response = (
            supabase.table("farmers")
            .select("*")
            .eq("id", farmer_id)
            .single()
            .execute()
        )
        return {"data": response.data}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{farmer_id}")
async def update_farmer(farmer_id: str, farmer: FarmerUpdate):
    try:
        response = (
            supabase.table("farmers")
            .update(farmer.model_dump(exclude_unset=True))
            .eq("id", farmer_id)
            .execute()
        )
        return {"message": "Farmer updated", "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{farmer_id}")
async def delete_farmer(farmer_id: str):
    try:
        supabase.table("farmers").delete().eq("id", farmer_id).execute()
        return {"message": "Farmer deleted"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
