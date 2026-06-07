from sqlalchemy import Column, Integer, String, Time, Boolean, DateTime, UniqueConstraint
from datetime import datetime, timezone
from app.models.student import Base

class ClassTiming(Base):
    __tablename__ = "class_timings"

    id = Column(Integer, primary_key=True, index=True)
    department = Column(String(50), nullable=True, index=True) # NULL means global default
    semester = Column(Integer, nullable=True, index=True)      # NULL means global default
    
    class_start_time = Column(Time, nullable=False)
    class_end_time = Column(Time, nullable=False)
    present_cutoff = Column(Time, nullable=False)
    late_cutoff = Column(Time, nullable=False)
    
    is_active = Column(Boolean, default=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint("department", "semester", name="uq_class_timing_dept_sem"),
    )

    def __repr__(self):
        return f"<ClassTiming(dept={self.department}, sem={self.semester}, start={self.class_start_time}, end={self.class_end_time})>"
