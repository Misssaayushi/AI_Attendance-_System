from fastapi import APIRouter
from app.routes import health

# Initialize the master API router
api_router = APIRouter()

# Include health routes
api_router.include_router(health.router, prefix="/health", tags=["Health"])