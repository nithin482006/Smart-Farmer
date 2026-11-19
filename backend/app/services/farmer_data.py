import time
from typing import List, Dict, Any, Optional
from app.database import get_supabase
from app.schemas.farm import FarmResponse, FarmCreate
from app.schemas.crops import CropCycleResponse, CropCycleCreate, CropGrowthStage
from app.schemas.weather import CurrentWeather, WeatherForecastDay, HistoricalWeatherPoint
from app.schemas.risk import CropRiskAlert
from app.schemas.market import MarketPrice
from app.schemas.dashboard import DashboardResponse, DashboardFarm, DashboardCrop

# In-memory session store for newly created farms and crop cycles during current runtime
SESSION_FARMS: List[Dict[str, Any]] = [
    {
        "id": "farm_001",
        "name": "Green Valley Fields",
        "state": "Karnataka",
        "district": "Bengaluru Rural",
        "village": "Doddaballapura",
        "latitude": 13.2984,
        "longitude": 77.5358,
        "land_area": 4.5,
        "area_unit": "Acres",
        "is_primary": True,
        "farmer_id": "farmer_demo_001",
    },
    {
        "id": "farm_002",
        "name": "Cauvery Riverside Farm",
        "state": "Karnataka",
        "district": "Mandya",
        "village": "Srirangapatna",
        "latitude": 12.4224,
        "longitude": 76.6833,
        "land_area": 6.0,
        "area_unit": "Acres",
        "is_primary": False,
        "farmer_id": "farmer_demo_001",
    },
]

SESSION_CROP_CYCLES: List[Dict[str, Any]] = [
    {
        "id": "cycle_001",
        "farm_id": "farm_001",
        "crop_name": "Paddy (Rice)",
        "variety": "BPT 5204 (Samba Mahsuri)",
        "sowing_date": "2026-08-25",
        "current_stage": "Flowering",
        "target_harvest_date": "2026-12-15",
        "expected_yield_tons": 3.8,
    },
    {
        "id": "cycle_002",
        "farm_id": "farm_002",
        "crop_name": "Sugarcane",
        "variety": "Co 86032",
        "sowing_date": "2026-02-10",
        "current_stage": "Vegetative",
        "target_harvest_date": "2027-01-20",
        "expected_yield_tons": 55.0,
    },
]

DEFAULT_WEATHER: Dict[str, Any] = {
    "temperature_c": 26,
    "temp_min_c": 19,
    "temp_max_c": 29,
    "humidity": 75,
    "rainfall_mm": 14,
    "wind_speed_kmh": 12,
    "rain_probability": 75,
    "condition": "Thunderstorms / Overcast",
    "source": "IMD (India Meteorological Department)",
    "updated_at": "2026-11-19T10:00:00Z",
}

DEFAULT_FORECAST: List[Dict[str, Any]] = [
    {
        "date": "2026-11-19",
        "day_name": "Today",
        "temp_max_c": 29,
        "temp_min_c": 19,
        "rainfall_probability": 75,
        "rainfall_expected_mm": 14,
        "condition": "Thunderstorms / Heavy Showers",
        "risk_level": "high",
    },
    {
        "date": "2026-11-20",
        "day_name": "Tomorrow",
        "temp_max_c": 28,
        "temp_min_c": 18,
        "rainfall_probability": 60,
        "rainfall_expected_mm": 8,
        "condition": "Scattered Showers",
        "risk_level": "moderate",
    },
    {
        "date": "2026-11-21",
        "day_name": "Fri",
        "temp_max_c": 30,
        "temp_min_c": 19,
        "rainfall_probability": 30,
        "rainfall_expected_mm": 2,
        "condition": "Partly Cloudy",
        "risk_level": "low",
    },
    {
        "date": "2026-11-22",
        "day_name": "Sat",
        "temp_max_c": 31,
        "temp_min_c": 20,
        "rainfall_probability": 15,
        "rainfall_expected_mm": 0,
        "condition": "Sunny / Clear",
        "risk_level": "low",
    },
    {
        "date": "2026-11-23",
        "day_name": "Sun",
        "temp_max_c": 30,
        "temp_min_c": 19,
        "rainfall_probability": 20,
        "rainfall_expected_mm": 0,
        "condition": "Mostly Clear",
        "risk_level": "low",
    },
]

DEFAULT_HISTORICAL: List[Dict[str, Any]] = [
    {"date": "2026-11-14", "rainfall_mm": 0, "temp_avg_c": 27.5, "humidity_avg": 62},
    {"date": "2026-11-15", "rainfall_mm": 2.5, "temp_avg_c": 26.8, "humidity_avg": 68},
    {"date": "2026-11-16", "rainfall_mm": 18.0, "temp_avg_c": 24.5, "humidity_avg": 82},
    {"date": "2026-11-17", "rainfall_mm": 32.4, "temp_avg_c": 23.2, "humidity_avg": 88},
    {"date": "2026-11-18", "rainfall_mm": 11.2, "temp_avg_c": 25.0, "humidity_avg": 79},
]

DEFAULT_RISKS: List[Dict[str, Any]] = [
    {
        "id": "alert_01",
        "crop_name": "Paddy (Rice)",
        "crop_stage": "Flowering",
        "hazard": "Heavy Rainfall & Pollen Washout Warning",
        "severity": "high",
        "reason": "Forecast rainfall of 14-22mm coincides with active flowering. Rain wash-out prevents pollination.",
        "advisory": "Ensure drainage channels in paddy basins are clear. Postpone urea top-dressing and chemical sprays.",
        "forecast_period": "Next 24 to 48 Hours",
        "source": "IMD Agromet Advisory Service",
        "timestamp": "2026-11-19T08:30:00Z",
        "is_read": False,
    },
    {
        "id": "alert_02",
        "crop_name": "Paddy (Rice)",
        "crop_stage": "Flowering",
        "hazard": "Bacterial Leaf Blight (BLB) Favorable Humidity",
        "severity": "moderate",
        "reason": "Extended relative humidity above 80% creates high disease pressure for Xanthomonas oryzae.",
        "advisory": "Avoid nitrogen excess. Monitor leaf tips for water-soaked yellow lesions; spray recommended biocontrols upon weather clearing.",
        "forecast_period": "Next 3 to 5 Days",
        "source": "ICAR Agromet Field Unit",
        "timestamp": "2026-11-18T14:00:00Z",
        "is_read": False,
    },
]

DEFAULT_MARKET_PRICES: List[Dict[str, Any]] = [
    {
        "id": "mkt_01",
        "commodity": "Paddy (Dhan) - Common",
        "state": "Karnataka",
        "district": "Bengaluru Rural",
        "mandi_name": "Doddaballapura APMC",
        "min_price": 2180,
        "max_price": 2350,
        "modal_price": 2280,
        "unit": "Quintal",
        "reporting_date": "2026-11-18",
        "trend": "up",
        "change_percentage": 2.4,
    },
    {
        "id": "mkt_02",
        "commodity": "Maize (Makka)",
        "state": "Karnataka",
        "district": "Bengaluru Rural",
        "mandi_name": "Doddaballapura APMC",
        "min_price": 1950,
        "max_price": 2150,
        "modal_price": 2080,
        "unit": "Quintal",
        "reporting_date": "2026-11-18",
        "trend": "stable",
        "change_percentage": 0.5,
    },
    {
        "id": "mkt_03",
        "commodity": "Ragi (Finger Millet)",
        "state": "Karnataka",
        "district": "Bengaluru Rural",
        "mandi_name": "Channapatna Mandi",
        "min_price": 3400,
        "max_price": 3850,
        "modal_price": 3650,
        "unit": "Quintal",
        "reporting_date": "2026-11-18",
        "trend": "up",
        "change_percentage": 3.8,
    },
    {
        "id": "mkt_04",
        "commodity": "Tomato",
        "state": "Karnataka",
        "district": "Kolar",
        "mandi_name": "Kolar APMC Market",
        "min_price": 1200,
        "max_price": 1800,
        "modal_price": 1550,
        "unit": "Quintal",
        "reporting_date": "2026-11-18",
        "trend": "down",
        "change_percentage": -4.2,
    },
]


class FarmerDataService:
    @staticmethod
    def get_farms(user_id: str) -> List[FarmResponse]:
        client = get_supabase()
        if client:
            try:
                res = client.table("farms").select("*").eq("farmer_id", user_id).execute()
                if res.data and len(res.data) > 0:
                    return [
                        FarmResponse(
                            id=row["id"],
                            name=row["name"],
                            state=row.get("state", "Karnataka"),
                            district=row.get("district", "Bengaluru Rural"),
                            village=row.get("location_name"),
                            latitude=float(row["latitude"]),
                            longitude=float(row["longitude"]),
                            land_area=float(row.get("total_area_acres") or 4.5),
                            area_unit="Acres",
                            is_primary=True,
                            farmer_id=row.get("farmer_id"),
                        )
                        for row in res.data
                    ]
            except Exception:
                pass

        # Return session farms
        return [FarmResponse(**f) for f in SESSION_FARMS]

    @staticmethod
    def create_farm(farm: FarmCreate, user_id: str) -> FarmResponse:
        new_id = f"farm_{int(time.time() * 1000)}"
        farm_dict = farm.model_dump()
        farm_dict["id"] = new_id
        farm_dict["farmer_id"] = user_id

        client = get_supabase()
        if client:
            try:
                client.table("farms").insert({
                    "id": new_id,
                    "farmer_id": user_id,
                    "name": farm.name,
                    "location_name": farm.village or farm.district,
                    "latitude": farm.latitude,
                    "longitude": farm.longitude,
                    "total_area_acres": farm.land_area,
                }).execute()
            except Exception:
                pass

        SESSION_FARMS.append(farm_dict)
        return FarmResponse(**farm_dict)

    @staticmethod
    def get_dashboard(farm_id: str) -> DashboardResponse:
        farm = next((f for f in SESSION_FARMS if f["id"] == farm_id), SESSION_FARMS[0])
        cycle = next((c for c in SESSION_CROP_CYCLES if c["farm_id"] == farm_id), SESSION_CROP_CYCLES[0])

        return DashboardResponse(
            farm=DashboardFarm(
                id=farm["id"],
                name=farm["name"],
                district=farm["district"],
                state=farm["state"],
                land_area=farm["land_area"],
                area_unit=farm.get("area_unit", "Acres"),
            ),
            weather=CurrentWeather(**DEFAULT_WEATHER),
            crop=DashboardCrop(
                name=cycle["crop_name"],
                variety=cycle.get("variety"),
                stage=cycle["current_stage"],
                sowing_date=cycle.get("sowing_date"),
            ),
            risks=[CropRiskAlert(**r) for r in DEFAULT_RISKS],
            market_prices=[MarketPrice(**p) for p in DEFAULT_MARKET_PRICES],
            upcoming_forecast=[WeatherForecastDay(**f) for f in DEFAULT_FORECAST],
        )

    @staticmethod
    def create_crop_cycle(cycle: CropCycleCreate) -> CropCycleResponse:
        new_id = f"cycle_{int(time.time() * 1000)}"
        cycle_dict = cycle.model_dump()
        cycle_dict["id"] = new_id

        client = get_supabase()
        if client:
            try:
                client.table("crop_cycles").insert({
                    "id": new_id,
                    "farm_id": cycle.farm_id,
                    "variety": cycle.variety,
                    "sowing_date": cycle.sowing_date,
                    "current_stage": cycle.current_stage.lower(),
                }).execute()
            except Exception:
                pass

        SESSION_CROP_CYCLES.append(cycle_dict)
        return CropCycleResponse(**cycle_dict)

    @staticmethod
    def update_crop_stage(cycle_id: str, stage: CropGrowthStage) -> bool:
        for c in SESSION_CROP_CYCLES:
            if c["id"] == cycle_id:
                c["current_stage"] = stage
                return True
        # If not matched, update the default active cycle
        if SESSION_CROP_CYCLES:
            SESSION_CROP_CYCLES[0]["current_stage"] = stage
        return True

    @staticmethod
    def get_weather(farm_id: str) -> Dict[str, Any]:
        return {
            "current": CurrentWeather(**DEFAULT_WEATHER),
            "forecast": [WeatherForecastDay(**f) for f in DEFAULT_FORECAST],
            "historical": [HistoricalWeatherPoint(**h) for h in DEFAULT_HISTORICAL],
        }

    @staticmethod
    def get_risks(farm_id: str) -> List[CropRiskAlert]:
        return [CropRiskAlert(**r) for r in DEFAULT_RISKS]

    @staticmethod
    def get_market_prices(commodity: Optional[str] = None, district: Optional[str] = None) -> List[MarketPrice]:
        prices = DEFAULT_MARKET_PRICES
        if commodity:
            prices = [p for p in prices if commodity.lower() in p["commodity"].lower()]
        if district:
            prices = [p for p in prices if district.lower() in p["district"].lower()]
        return [MarketPrice(**p) for p in prices]

    @staticmethod
    def get_alerts() -> List[CropRiskAlert]:
        return [CropRiskAlert(**r) for r in DEFAULT_RISKS]

    @staticmethod
    def mark_alert_read(alert_id: str) -> bool:
        for r in DEFAULT_RISKS:
            if r["id"] == alert_id:
                r["is_read"] = True
                return True
        return True
