from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.middleware.auth_deps import get_current_admin
from app.schemas.class_timing import ClassTimingCreate, ClassTimingResponse, ClassTimingListResponse
from app.services import class_timing_service
from app.utils.logger import logger
from app.utils.response import success, success_response

router = APIRouter(dependencies=[Depends(get_current_admin)])

@router.get("/")
def list_class_timings(db: Session = Depends(get_db)):
    logger.info("event=class_timings_list_request")
    records = class_timing_service.get_all_timings(db)
    items = [ClassTimingResponse.model_validate(r).model_dump(mode="json") for r in records]
    return success(data={"items": items, "total": len(items)}, message="Class timings retrieved successfully")

@router.post("/", status_code=status.HTTP_201_CREATED)
def upsert_class_timing(
    payload: ClassTimingCreate,
    db: Session = Depends(get_db)
):
    logger.info("event=class_timing_upsert_request dept=%s sem=%s", payload.department, payload.semester)
    record = class_timing_service.upsert_timing(db, payload)
    return success_response(
        data=ClassTimingResponse.model_validate(record).model_dump(mode="json"), 
        message="Class timing rule saved successfully",
        status_code=201
    )

@router.delete("/{timing_id}")
def delete_class_timing(timing_id: int, db: Session = Depends(get_db)):
    logger.info("event=class_timing_delete_request timing_id=%s", timing_id)
    class_timing_service.delete_timing(db, timing_id)
    return success(data={"id": timing_id}, message="Class timing rule deleted successfully")
