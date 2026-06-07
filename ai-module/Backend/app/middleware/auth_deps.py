from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.config import settings
from app.database.connection import get_db
from app.models.admin import Admin
from app.schemas.auth import TokenData
import logging

logger = logging.getLogger("ai_attendance")

# This tells FastAPI to look for a 'Bearer' token in the Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_PREFIX}/auth/login")

def get_current_admin(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Admin:
    """
    Dependency that validates a JWT token and returns the current admin.
    Use this to protect routes.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 1. Decode token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        
        if username is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
        
    # 2. Fetch admin from DB to ensure they still exist/are active
    admin = db.query(Admin).filter(Admin.username == username).first()
    
    if admin is None:
        raise credentials_exception
        
    return admin
