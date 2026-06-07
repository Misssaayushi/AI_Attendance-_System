from sqlalchemy.orm import Session
from app.models.admin import Admin
from app.utils.security import verify_password
from fastapi import HTTPException, status

def authenticate_admin(db: Session, username: str, password: str) -> Admin:
    """
    Validates admin credentials.
    1. Fetches admin by username.
    2. Verifies hashed password.
    Returns Admin object if successful, otherwise raises 401.
    """
    # 1. Fetch admin record
    admin = db.query(Admin).filter(Admin.username == username).first()
    
    # 2. Check if admin exists
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. Verify password hash
    if not verify_password(password, admin.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    return admin
