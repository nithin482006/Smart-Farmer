from fastapi import APIRouter

router = APIRouter()


@router.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "message": "Smart Farmer backend is running!",
        "service": "Smart Farmer API"
    }
