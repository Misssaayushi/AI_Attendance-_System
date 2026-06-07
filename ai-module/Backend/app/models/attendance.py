from sqlalchemy import Column, Integer, String, Date, Time, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.models.student import Base

class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    
    date = Column(Date, default=lambda: datetime.now(timezone.utc).date(), index=True)
    time = Column(Time, default=lambda: datetime.now(timezone.utc).time())
    status = Column(String(20), default="Present", index=True) # Present, Absent, Late

    # Relationship back to student
    student = relationship("Student", back_populates="attendance_records")

    # Composite index for faster searching by student and date
    __table_args__ = (
        Index('idx_student_date', 'student_id', 'date'),
    )

    def __repr__(self):
        return f"<Attendance(student_id={self.student_id}, date={self.date}, status={self.status})>"
