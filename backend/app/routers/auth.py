from fastapi import APIRouter, HTTPException
from app.database import get_supabase
from app.models.schemas import UserSignUp, UserSignIn

router = APIRouter()


@router.post("/signup")
async def sign_up(user: UserSignUp):
    client = get_supabase()
    if not client:
        return {
            "message": "Demo mode: user created successfully",
            "user_id": "demo_user_new",
            "email": user.email,
        }
    try:
        response = client.auth.sign_up({
            "email": user.email,
            "password": user.password,
            "options": {
                "data": {
                    "full_name": user.full_name,
                    "phone": user.phone,
                }
            }
        })
        return {
            "message": "User created successfully",
            "user_id": response.user.id if response and response.user else "demo_id",
            "email": user.email,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/signin")
async def sign_in(user: UserSignIn):
    client = get_supabase()
    if not client:
        return {
            "message": "Demo mode: signed in successfully",
            "access_token": "demo_jwt_token_sample",
            "refresh_token": "demo_refresh_token_sample",
            "user_id": "farmer_demo_001",
        }
    try:
        response = client.auth.sign_in_with_password({
            "email": user.email,
            "password": user.password,
        })
        return {
            "message": "Signed in successfully",
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "user_id": response.user.id,
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/signout")
async def sign_out():
    client = get_supabase()
    if client:
        try:
            client.auth.sign_out()
        except Exception:
            pass
    return {"message": "Signed out successfully"}
