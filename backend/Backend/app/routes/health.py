from fastapi import APIRouter, Depends
from app.utils.response import success_response
from app.database.connection import test_db_connection

router = APIRouter()

@router.get("")
async def health_check():
    """
    Health check endpoint to verify server and database status.
    """
    db_status = "connected" if test_db_connection() else "disconnected"
    
    health_data = {
        "server": "online",
        "database": db_status,
        "version": "1.0.0"
    }
    
    return success_response(
        data=health_data,
        message="System health check successful"
    )
