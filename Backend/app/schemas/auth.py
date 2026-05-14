from pydantic import BaseModel, Field

class LoginRequest(BaseModel):
    """Schema for incoming login requests."""
    username: str = Field(..., json_schema_extra={"example": "admin"})
    password: str = Field(..., json_schema_extra={"example": "password123"})

class TokenResponse(BaseModel):
    """Schema for successful login responses."""
    success: bool = True
    message: str = "Login Successful"
    access_token: str
    token_type: str = "bearer"
    username: str

class LogoutResponse(BaseModel):
    """Schema for logout responses."""
    success: bool = True
    message: str = "Logged Out Successfully"

class TokenData(BaseModel):
    """Schema for internal token payload verification."""
    username: str
    exp: int
