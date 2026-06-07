from typing import Optional, Tuple
from datetime import time
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.repositories import class_timing_repository
from app.models.class_timing import ClassTiming
from app.schemas.class_timing import ClassTimingCreate, ClassTimingUpdate
from app.utils.logger import logger
from app.exceptions import BadRequestException, NotFoundException

# Hardcoded fallbacks if no rules exist in DB
DEFAULT_PRESENT_CUTOFF = time(9, 0, 0)
DEFAULT_LATE_CUTOFF = time(11, 30, 0)
DEFAULT_CLASS_START = time(8, 0, 0)
DEFAULT_CLASS_END = time(16, 0, 0) # Fallback to 4 PM for auto-absent

def resolve_timing(db: Session, department: Optional[str] = None, semester: Optional[int] = None) -> Tuple[time, time, time, time]:
    """
    Resolves the applicable timing rules for a given department and semester.
    Fallback chain:
    1. Exact match (department + semester)
    2. Global default (department=None, semester=None)
    3. Hardcoded default
    
    Returns: (class_start_time, class_end_time, present_cutoff, late_cutoff)
    """
    # 1. Try exact match if both provided
    if department is not None or semester is not None:
        rule = class_timing_repository.get_by_dept_and_sem(db, department, semester)
        if rule and rule.is_active:
            return rule.class_start_time, rule.class_end_time, rule.present_cutoff, rule.late_cutoff
            
    # 2. Try global default (both None)
    global_rule = class_timing_repository.get_by_dept_and_sem(db, None, None)
    if global_rule and global_rule.is_active:
        return global_rule.class_start_time, global_rule.class_end_time, global_rule.present_cutoff, global_rule.late_cutoff
        
    # 3. Hardcoded fallback
    return DEFAULT_CLASS_START, DEFAULT_CLASS_END, DEFAULT_PRESENT_CUTOFF, DEFAULT_LATE_CUTOFF

def get_all_timings(db: Session) -> list[ClassTiming]:
    return class_timing_repository.get_all(db)

def get_timing(db: Session, timing_id: int) -> ClassTiming:
    rule = class_timing_repository.get_by_id(db, timing_id)
    if not rule:
        raise NotFoundException("Class timing rule not found")
    return rule

def upsert_timing(db: Session, payload: ClassTimingCreate) -> ClassTiming:
    """Creates or updates a rule for the specific dept/sem combo."""
    existing = class_timing_repository.get_by_dept_and_sem(db, payload.department, payload.semester)
    try:
        if existing:
            update_payload = ClassTimingUpdate(**payload.model_dump())
            record = class_timing_repository.update(db, existing, update_payload)
            logger.info("event=class_timing_updated id=%s dept=%s sem=%s", record.id, record.department, record.semester)
            return record
        else:
            record = class_timing_repository.create(db, payload)
            logger.info("event=class_timing_created id=%s dept=%s sem=%s", record.id, record.department, record.semester)
            return record
    except IntegrityError as exc:
        db.rollback()
        logger.error("event=class_timing_upsert_failed error=%s", str(exc))
        raise BadRequestException("Failed to save class timing rule (database integrity error)") from exc

def delete_timing(db: Session, timing_id: int) -> None:
    success = class_timing_repository.delete(db, timing_id)
    if not success:
        raise NotFoundException("Class timing rule not found")
    logger.info("event=class_timing_deleted id=%s", timing_id)
