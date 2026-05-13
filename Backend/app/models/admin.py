from sqlalchemy import Column, Integer, String
from app.models.student import Base

class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False) # Will store hashed password later

    def __repr__(self):
        return f"<Admin(username={self.username})>"
