from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime, timezone

Base = declarative_base()

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    roll_number = Column(String(50), unique=True, index=True, nullable=False)
    email_address = Column(String(100), unique=True, index=True, nullable=False)
    contact_number = Column(String(20), nullable=True)
    
    # Dropdown-compatible fields
    department = Column(String(50), index=True, nullable=False)
    course = Column(String(100), nullable=False)
    year_batch = Column(String(20), nullable=False)
    semester = Column(Integer, nullable=False)
    section = Column(String(10), nullable=True)
    gender = Column(String(20), nullable=False)
    
    # AI/Face Recognition Field
    # Stores the numerical face encoding (e.g., JSON string or binary)
    face_encoding = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    # cascade="all, delete-orphan" means if a student is deleted, their attendance is too
    attendance_records = relationship("Attendance", back_populates="student", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Student(name={self.full_name}, roll={self.roll_number})>"
