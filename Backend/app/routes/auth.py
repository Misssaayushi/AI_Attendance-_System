from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.auth import LoginRequest, TokenResponse, LogoutResponse
from app.services.auth_service import authenticate_admin
from app.utils.security import create_access_token
from app.utils.logger import logger

from app.middleware.auth_deps import get_current_admin
from app.models.admin import Admin

router = APIRouter()

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Handle admin login and issue JWT token.
    """
    logger.info(f"🔑 Login attempt for user: {request.username}")
    
    # 1. Authenticate user via service layer
    admin = authenticate_admin(db, request.username, request.password)
    
    # 2. Create JWT token
    access_token = create_access_token(data={"sub": admin.username})
    
    logger.info(f"✅ Login successful for user: {request.username}")
    
    return {
        "success": True,
        "message": "Login Successful",
        "access_token": access_token,
        "token_type": "bearer",
        "username": admin.username
    }

@router.get("/me")
async def get_me(current_admin: Admin = Depends(get_current_admin)):
    """
    A protected route that returns the current logged-in admin's info.
    This verifies that our route protection (Phase 3 Step 5) is working.
    """
    return {
        "success": True,
        "username": current_admin.username,
        "id": current_admin.id
    }

@router.post("/logout", response_model=LogoutResponse)
async def logout():
    """
    Logout endpoint. 
    Note: JWT is stateless, so logout is primarily handled by the client 
    discarding the token.
    """
    return {
        "success": True,
        "message": "Logged Out Successfully"
    }
