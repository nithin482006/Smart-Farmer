from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# --- Auth Models ---
class UserSignUp(BaseModel):
    email: str
    password: str
    full_name: str
    phone: Optional[str] = None


class UserSignIn(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    phone: Optional[str] = None
    created_at: Optional[datetime] = None


# --- Farmer Models ---
class FarmerCreate(BaseModel):
    full_name: str
    phone: str
    location: str
    farm_size_acres: Optional[float] = None
    experience_years: Optional[int] = None


class FarmerUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    farm_size_acres: Optional[float] = None
    experience_years: Optional[int] = None


class FarmerResponse(BaseModel):
    id: str
    user_id: str
    full_name: str
    phone: str
    location: str
    farm_size_acres: Optional[float] = None
    experience_years: Optional[int] = None
    created_at: Optional[datetime] = None


# --- Crop Models ---
class CropCreate(BaseModel):
    name: str
    variety: Optional[str] = None
    season: str  # kharif, rabi, zaid
    sowing_date: Optional[str] = None
    expected_harvest_date: Optional[str] = None
    area_acres: Optional[float] = None
    status: str = "planned"  # planned, sown, growing, harvested


class CropUpdate(BaseModel):
    name: Optional[str] = None
    variety: Optional[str] = None
    season: Optional[str] = None
    sowing_date: Optional[str] = None
    expected_harvest_date: Optional[str] = None
    area_acres: Optional[float] = None
    status: Optional[str] = None


class CropResponse(BaseModel):
    id: str
    farmer_id: str
    name: str
    variety: Optional[str] = None
    season: str
    sowing_date: Optional[str] = None
    expected_harvest_date: Optional[str] = None
    area_acres: Optional[float] = None
    status: str
    created_at: Optional[datetime] = None


# --- Market Models ---
class MarketPriceCreate(BaseModel):
    crop_name: str
    price_per_quintal: float
    market_name: str
    location: str


class MarketPriceResponse(BaseModel):
    id: str
    crop_name: str
    price_per_quintal: float
    market_name: str
    location: str
    recorded_at: Optional[datetime] = None
