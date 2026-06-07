from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from datetime import datetime, timezone

from app.models.class_timing import ClassTiming
from app.schemas.class_timing import ClassTimingCreate, ClassTimingUpdate

def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[ClassTiming]:
    return db.query(ClassTiming).offset(skip).limit(limit).all()

def get_by_id(db: Session, timing_id: int) -> Optional[ClassTiming]:
    return db.query(ClassTiming).filter(ClassTiming.id == timing_id).first()

def get_by_dept_and_sem(db: Session, department: Optional[str], semester: Optional[int]) -> Optional[ClassTiming]:
    return db.query(ClassTiming).filter(
        ClassTiming.department == department,
        ClassTiming.semester == semester
    ).first()

def create(db: Session, obj_in: ClassTimingCreate) -> ClassTiming:
    db_obj = ClassTiming(
        department=obj_in.department,
        semester=obj_in.semester,
        class_start_time=obj_in.class_start_time,
        class_end_time=obj_in.class_end_time,
        present_cutoff=obj_in.present_cutoff,
        late_cutoff=obj_in.late_cutoff,
        is_active=obj_in.is_active
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update(db: Session, db_obj: ClassTiming, obj_in: ClassTimingUpdate) -> ClassTiming:
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db_obj.updated_at = datetime.now(timezone.utc)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete(db: Session, timing_id: int) -> bool:
    db_obj = get_by_id(db, timing_id)
    if db_obj:
        db.delete(db_obj)
        db.commit()
        return True
    return False

def get_active_rules(db: Session) -> List[ClassTiming]:
    return db.query(ClassTiming).filter(ClassTiming.is_active == True).all()
