from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.router import api_router
from app.routers import auth

app = FastAPI(
    title=settings.APP_NAME,
    description="FastAPI Backend for Smart Farmer — Crop-Stage Weather Intelligence & Mandi Prices",
    version="1.0.0",
    debug=settings.APP_DEBUG,
)

# CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Core v1 API Router matching frontend/BACKEND_INTEGRATION.md contract
app.include_router(api_router, prefix="/api/v1")

# Authentication Router
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])


@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "healthy",
        "service": "Smart Farmer API",
        "version": "1.0.0",
        "docs_url": "/docs",
    }


@app.get("/api/health", tags=["Health"])
async def health_check():
    return {
        "status": "ok",
        "environment": settings.APP_ENV,
        "service": "Smart Farmer API",
    }
