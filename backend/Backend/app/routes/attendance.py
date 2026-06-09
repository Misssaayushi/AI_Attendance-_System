from __future__ import annotations

from datetime import date, datetime

import os
import asyncio
from fastapi import APIRouter, Depends, Query, status, Header, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.exceptions import DuplicateAttendanceException
from app.middleware.auth_deps import get_current_admin
from app.schemas import attendance as attendance_schema
from app.services import attendance_service
from app.services import auto_absent_service
from app.services import email_service
from app.services import excel_service
from app.utils.logger import logger
from app.utils.request_validation import normalize_page_size, normalize_search
from app.utils.response import success, success_response
from app.routes.websocket import broadcast_attendance_event

router = APIRouter(dependencies=[Depends(get_current_admin)])
ai_router = APIRouter()

INTERNAL_API_KEY = os.getenv("AI_MODULE_API_KEY", "ai-module-secret-key")

@ai_router.post("/verify", status_code=status.HTTP_201_CREATED)
def verify_attendance_from_ai(
    payload: attendance_schema.AIAttendancePayload,
    background_tasks: BackgroundTasks,
    x_api_key: str = Header(..., alias="X-API-Key"),
    db: Session = Depends(get_db),
):
    """
    Endpoint for AI Module to send verified attendance events.
    Uses API key authentication instead of JWT.
    """
    if x_api_key != INTERNAL_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")

    # Convert AI payload to standard attendance mark request
    mark_request = attendance_schema.AttendanceMarkRequest(
        student_id=payload.student_id,
        confidence_score=payload.confidence / 100.0,  # Convert 0-100 -> 0.0-1.0
        source="ai_recognition",
    )
    
    record = attendance_service.mark_attendance(db, mark_request)
    
    # Broadcast real-time event to all connected Frontend clients
    event = {
        "type": "attendance_marked",
        "student_id": record.student_id,
        "student_name": record.student.full_name if record.student else payload.student_id,
        "status": record.status,
        "time": record.time.isoformat() if record.time else None,
        "confidence": payload.confidence,
    }
    background_tasks.add_task(broadcast_attendance_event, event)

    return success_response(
        data={"id": record.id, "student_id": record.student_id, "status": record.status},
        message="Attendance verified and logged",
        status_code=201,
    )

from pydantic import BaseModel

class UnrecognizedPayload(BaseModel):
    timestamp: str
    confidence: float

@ai_router.post("/unrecognized", status_code=status.HTTP_201_CREATED)
def handle_unrecognized_face(
    payload: UnrecognizedPayload,
    background_tasks: BackgroundTasks,
    x_api_key: str = Header(..., alias="X-API-Key"),
):
    """
    Endpoint for AI Module to send unrecognized face events.
    """
    if x_api_key != INTERNAL_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
        
    event = {
        "type": "unrecognized_face",
        "timestamp": payload.timestamp,
        "confidence": payload.confidence,
    }
    background_tasks.add_task(broadcast_attendance_event, event)
    
    return success_response(
        data=event,
        message="Unrecognized face event broadcasted",
        status_code=201,
    )

import tempfile
import base64
import json

_ai_detector = None
_ai_manager = None
_ai_recognizer = None

def get_ai_models():
    global _ai_detector, _ai_manager, _ai_recognizer
    if _ai_detector is None:
        from app.config import settings
        import sys
        if settings.AI_MODULE_DIR not in sys.path:
            sys.path.append(settings.AI_MODULE_DIR)
        
        try:
            from utils import FaceDetector, EncodingManager, FaceRecognizer
            from config import ENCODING_FILE, FACE_DETECTION_MODEL, FRAME_RESIZE_SCALE, RECOGNITION_TOLERANCE
            _ai_detector = FaceDetector(model=FACE_DETECTION_MODEL, scale=FRAME_RESIZE_SCALE)
            _ai_manager = EncodingManager(encoding_file=ENCODING_FILE)
            _ai_recognizer = FaceRecognizer(encoding_manager=_ai_manager, tolerance=RECOGNITION_TOLERANCE)
        except ImportError as e:
            raise RuntimeError(f"Could not load AI models: {e}")
            
    return _ai_detector, _ai_manager, _ai_recognizer


_dataset_cache = {}

@ai_router.post("/recognize-frame")
def recognize_frame(
    payload: attendance_schema.RecognizeFrameRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Endpoint for Web UI to send a frame and get it recognized.
    Checks all photos in the dataset folder directly to compare with the student in the camera.
    """
    import sys
    import os
    from app.config import settings

    # Inject AI Module's virtual environment site-packages to sys.path
    # so we can import face_recognition, dlib, and cv2 directly
    ai_venv_site = os.path.join(settings.AI_MODULE_DIR, "venv", "lib", f"python{sys.version_info.major}.{sys.version_info.minor}", "site-packages")
    if os.path.exists(ai_venv_site) and ai_venv_site not in sys.path:
        sys.path.append(ai_venv_site)

    import cv2
    import numpy as np
    import face_recognition

    # 1. Decode base64 image
    img_data = payload.image_base64
    if "," in img_data:
        img_data = img_data.split(",")[1]
    
    img_bytes = base64.b64decode(img_data)
    
    # 2. Convert to CV2 frame
    nparr = np.frombuffer(img_bytes, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if frame is None:
        return success_response(data={"status": "error", "message": "Failed to decode image"}, message="Recognition failed", status_code=500)

    try:
        # Dynamically check dataset folder and keep in cache
        global _dataset_cache
        dataset_dir = settings.AI_DATASET_DIR

        # 1. Prune folders from cache if they are no longer in the physical directory
        existing_folders = set()
        if os.path.exists(dataset_dir):
            existing_folders = {f for f in os.listdir(dataset_dir) if os.path.isdir(os.path.join(dataset_dir, f))}
        for cached_folder in list(_dataset_cache.keys()):
            if cached_folder not in existing_folders:
                del _dataset_cache[cached_folder]

        # 2. Get active student IDs from DB to filter out orphan directories
        from app.models.student import Student
        active_student_ids = {s.id for s in db.query(Student.id).all()}

        # 3. Load/update encodings from dataset folders
        if os.path.exists(dataset_dir):
            for student_folder in os.listdir(dataset_dir):
                folder_path = os.path.join(dataset_dir, student_folder)
                if os.path.isdir(folder_path):
                    # Parse student_id from folder name (e.g. "12_Aayushi" -> 12)
                    try:
                        student_id = int(student_folder.split('_')[0]) if '_' in student_folder else int(student_folder)
                    except ValueError:
                        continue

                    # Skip folders for students that do not exist in the database
                    if student_id not in active_student_ids:
                        if student_folder in _dataset_cache:
                            del _dataset_cache[student_folder]
                        continue

                    files = sorted(
                        f for f in os.listdir(folder_path)
                        if f.lower().endswith(('.jpg', '.jpeg', '.png'))
                    )
                    signature = tuple(
                        (
                            f,
                            os.path.getmtime(os.path.join(folder_path, f)),
                            os.path.getsize(os.path.join(folder_path, f)),
                        )
                        for f in files
                    )
                    cache_entry = _dataset_cache.get(student_folder)
                    cache_signature = cache_entry.get("signature") if isinstance(cache_entry, dict) else None

                    if cache_signature != signature:
                        encodings = []
                        # 1. Try to load pre-calculated individual student pickle
                        import pickle
                        from pathlib import Path
                        individual_pkl = Path(settings.AI_MODULE_DIR) / "encodings" / f"{student_folder}.pkl"
                        
                        if individual_pkl.exists():
                            try:
                                with open(individual_pkl, "rb") as f:
                                    encodings = pickle.load(f)
                                logger.info(f"Loaded cached encodings from pickle for student {student_folder}")
                            except Exception as e:
                                logger.warning(f"Failed to load pickle for {student_folder}, falling back to raw images: {e}")
                        
                        # 2. Fallback: calculate from raw images if pickle didn't exist or failed
                        if not encodings:
                            for img_name in files:
                                img_path = os.path.join(folder_path, img_name)
                                img = face_recognition.load_image_file(img_path)
                                face_locs = face_recognition.face_locations(img)
                                if face_locs:
                                    # Sort face locations by area (descending) to ensure we always grab the largest face (the student)
                                    face_locs.sort(key=lambda loc: (loc[1] - loc[3]) * (loc[2] - loc[0]), reverse=True)
                                    encs = face_recognition.face_encodings(img, [face_locs[0]])
                                    if encs:
                                        encodings.append(encs[0])
                        _dataset_cache[student_folder] = {
                            "signature": signature,
                            "encodings": encodings,
                        }

        # 3. Detect faces
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Resize for speed
        small_frame = cv2.resize(rgb_frame, (0, 0), fx=0.25, fy=0.25)
        face_locations_small = face_recognition.face_locations(small_frame)

        if not face_locations_small:
            results = []
            ai_response = {"status": "no_face_found"}
        else:
            face_locations = []
            for (top, right, bottom, left) in face_locations_small:
                face_locations.append((top * 4, right * 4, bottom * 4, left * 4))

            live_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
            
            # --- Multi-face recognition: match each face independently ---
            results = []
            matched_student_ids = set()  # Deduplicate within a single frame

            for face_loc, live_enc in zip(face_locations, live_encodings):
                face_best_name = "Unknown"
                face_best_confidence = 0.0

                for student_name, cache_entry in _dataset_cache.items():
                    photo_encodings = (
                        cache_entry.get("encodings", [])
                        if isinstance(cache_entry, dict)
                        else cache_entry
                    )
                    if not photo_encodings:
                        continue
                    distances = face_recognition.face_distance(photo_encodings, live_enc)
                    if len(distances) == 0:
                        continue
                    match_idx = int(np.argmin(distances))
                    distance = float(distances[match_idx])
                    if distance <= 0.5:
                        confidence = max(0, (0.5 - distance) / 0.5) * 100
                        final_confidence = 75 + (confidence * 0.24)

                        if final_confidence > face_best_confidence:
                            face_best_confidence = final_confidence
                            face_best_name = student_name

                if face_best_name in ("Unknown", "Unknown Person"):
                    results.append({
                        "type": "unrecognized",
                        "status": "unrecognized",
                        "box": face_loc,
                        "confidence": 0.0,
                        "message": "Student should register first.",
                    })
                else:
                    try:
                        student_id = int(face_best_name.split('_')[0] if '_' in face_best_name else face_best_name)
                    except (ValueError, TypeError):
                        results.append({
                            "type": "error",
                            "status": "error",
                            "box": face_loc,
                            "message": f"Could not parse student ID from '{face_best_name}'",
                        })
                        continue

                    # Deduplicate: skip if this student was already matched to another face in this frame
                    if student_id in matched_student_ids:
                        continue
                    matched_student_ids.add(student_id)

                    # Attempt to mark attendance
                    mark_request = attendance_schema.AttendanceMarkRequest(
                        student_id=student_id,
                        confidence_score=face_best_confidence / 100.0,
                        source="web_ui_recognition",
                    )
                    try:
                        record = attendance_service.mark_attendance(db, mark_request)
                        event = {
                            "type": "attendance_marked",
                            "student_id": record.student_id,
                            "student_name": record.student.full_name if record.student else str(student_id),
                            "status": record.status,
                            "time": record.time.isoformat() if record.time else None,
                            "confidence": face_best_confidence,
                            "box": face_loc,
                        }
                        background_tasks.add_task(broadcast_attendance_event, event)
                        results.append(event)
                    except DuplicateAttendanceException as e:
                        existing = attendance_service.get_student_attendance_for_date(db, student_id=student_id)
                        results.append({
                            "type": "attendance_duplicate",
                            "status": "duplicate",
                            "student_id": student_id,
                            "student_name": existing.student.full_name if existing and existing.student else str(student_id),
                            "time": existing.time.isoformat() if existing and existing.time else None,
                            "confidence": face_best_confidence,
                            "box": face_loc,
                            "message": str(e),
                        })
                    except Exception as e:
                        results.append({
                            "type": "error",
                            "status": "error",
                            "student_id": student_id,
                            "box": face_loc,
                            "message": str(e),
                        })

            # Build the multi-recognition response
            if not results:
                return success_response(
                    data={"status": "no_face_found"},
                    message="No actionable face found",
                    status_code=200,
                )

            # Backward compatibility: if only one face was detected, return the legacy single-result shape
            if len(results) == 1:
                single = results[0]
                if single.get("type") == "attendance_marked":
                    return success_response(data=single, message="Match found", status_code=200)
                elif single.get("status") == "duplicate":
                    return success_response(data=single, message=single.get("message", "Already marked"), status_code=200)
                elif single.get("status") == "unrecognized":
                    return success_response(data=single, message="Unknown person, please first register yourself", status_code=200)
                else:
                    return success_response(data=single, message=single.get("message", "Error"), status_code=200)

            # Multi-face response
            return success_response(
                data={
                    "type": "multi_recognition",
                    "faces_detected": len(face_locations),
                    "results": results,
                },
                message=f"{len(results)} faces processed",
                status_code=200,
            )
    except Exception as e:
        return success_response(data={"status": "error", "message": str(e)}, message="Recognition failed", status_code=500)
            
def _serialize_record(record) -> dict:
    data = attendance_schema.AttendanceRecordResponse(
        id=record.id,
        student_id=record.student_id,
        student_name=record.student.full_name if record.student else None,
        roll_number=record.student.roll_number if record.student else None,
        attendance_date=record.date,
        attendance_time=record.time,
        status=record.status,
        confidence_score=None,
        source=None,
        created_at=None,
    ).model_dump(mode="json")
    data["department"] = record.student.department if record.student else None
    return data


@router.post("/mark", status_code=status.HTTP_201_CREATED)
def mark_attendance(
    payload: attendance_schema.AttendanceMarkRequest,
    db: Session = Depends(get_db),
):
    logger.info(
        "event=attendance_mark_request student_id=%s status=%s confidence=%s source=%s",
        payload.student_id,
        payload.status.value,
        payload.confidence_score,
        payload.source,
    )
    record = attendance_service.mark_attendance(db, payload)
    response = attendance_schema.AttendanceMarkResponse(
        id=record.id,
        student_id=record.student_id,
        attendance_date=record.date,
        attendance_time=record.time,
        status=record.status,
        confidence_score=payload.confidence_score,
        source=payload.source,
        message="Attendance marked successfully",
    ).model_dump(mode="json")
    return success_response(data=response, message="Attendance marked successfully", status_code=201)


@router.get("/")
def list_attendance(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    student_id: int | None = Query(default=None, gt=0),
    department: str | None = None,
    search: str | None = None,
    status: attendance_schema.AttendanceStatus | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
    db: Session = Depends(get_db),
):
    page_size = normalize_page_size(page_size)
    search = normalize_search(search)
    logger.info(
        "event=attendance_list_request page=%s page_size=%s student_id=%s department=%s status=%s from_date=%s to_date=%s search=%s",
        page,
        page_size,
        student_id,
        department,
        status.value if status else None,
        from_date,
        to_date,
        search,
    )
    records, total = attendance_service.list_attendance(
        db,
        page=page,
        page_size=page_size,
        student_id=student_id,
        department=department,
        search=search,
        status=status.value if status else None,
        from_date=from_date,
        to_date=to_date,
    )
    serialized_items = [_serialize_record(r) for r in records]
    response = attendance_service.build_paginated_response(serialized_items, total, page, page_size)
    return success(data=response, message="Attendance records retrieved successfully")


@ai_router.get("/summary/daily")
def daily_summary(
    target_date: date | None = None,
    db: Session = Depends(get_db),
):
    logger.info("event=attendance_daily_summary_request target_date=%s", target_date)
    summary = attendance_service.get_daily_summary(db, target_date=target_date)
    return success(data=summary.model_dump(mode="json"), message="Daily attendance summary retrieved successfully")


@router.get("/student/{student_id}")
def get_student_attendance(
    student_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    from_date: date | None = None,
    to_date: date | None = None,
    db: Session = Depends(get_db),
):
    page_size = normalize_page_size(page_size)
    logger.info(
        "event=student_attendance_request student_id=%s page=%s page_size=%s from_date=%s to_date=%s",
        student_id,
        page,
        page_size,
        from_date,
        to_date,
    )
    records, total = attendance_service.list_attendance(
        db,
        page=page,
        page_size=page_size,
        student_id=student_id,
        from_date=from_date,
        to_date=to_date,
    )
    serialized_items = [_serialize_record(r) for r in records]
    response = attendance_service.build_paginated_response(serialized_items, total, page, page_size)
    return success(data=response, message="Student attendance records retrieved successfully")


@router.get("/export/preview")
def export_preview(
    from_date: date | None = None,
    to_date: date | None = None,
    student_id: int | None = Query(default=None, gt=0),
    db: Session = Depends(get_db),
):
    logger.info(
        "event=attendance_export_preview_request from_date=%s to_date=%s student_id=%s",
        from_date,
        to_date,
        student_id,
    )
    rows = attendance_service.build_export_preview(
        db,
        from_date=from_date,
        to_date=to_date,
        student_id=student_id,
    )
    return success(data={"rows": rows, "count": len(rows)}, message="Attendance export preview generated")


@router.post("/export/monthly")
def export_monthly_workbook(
    year: int = Query(..., ge=2000, le=2100),
    month: int = Query(..., ge=1, le=12),
    department: str | None = None,
    student_id: int | None = Query(default=None, gt=0),
    db: Session = Depends(get_db),
):
    logger.info(
        "event=attendance_export_monthly_request year=%s month=%s department=%s student_id=%s",
        year,
        month,
        department,
        student_id,
    )
    if department:
        data = excel_service.generate_department_monthly_report(
            db,
            year=year,
            month=month,
            department=department,
        )
        return success(data=data, message="Department monthly workbook generated")

    if student_id:
        data = excel_service.generate_student_monthly_report(
            db,
            year=year,
            month=month,
            student_id=student_id,
        )
        return success(data=data, message="Student monthly workbook generated")

    data = excel_service.generate_monthly_workbook_from_db(db, year=year, month=month)
    return success(data=data, message="Monthly workbook generated")


@router.post("/export/template")
def export_monthly_template(
    year: int = Query(..., ge=2000, le=2100),
    month: int = Query(..., ge=1, le=12),
):
    logger.info("event=attendance_export_template_request year=%s month=%s", year, month)
    path = excel_service.generate_monthly_workbook_template(year=year, month=month)
    return success(data={"file_path": path, "year": year, "month": month}, message="Monthly template generated")


@router.post("/export/sync/{attendance_id}")
def sync_attendance_to_workbook(
    attendance_id: int,
    year: int = Query(..., ge=2000, le=2100),
    month: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db),
):
    logger.info(
        "event=attendance_export_sync_request attendance_id=%s year=%s month=%s",
        attendance_id,
        year,
        month,
    )
    data = excel_service.sync_attendance_record_to_monthly_workbook(
        db,
        attendance_id=attendance_id,
        year=year,
        month=month,
    )
    return success(data=data, message="Attendance record synced to workbook")


@router.get("/automation/executions")
def scheduler_executions(
    limit: int = Query(30, ge=1, le=200),
    db: Session = Depends(get_db),
):
    logger.info("event=scheduler_executions_list_request limit=%s", limit)
    rows = auto_absent_service.list_scheduler_executions(db, limit=limit)
    data = [
        {
            "id": row.id,
            "job_name": row.job_name,
            "run_date": row.run_date.isoformat(),
            "status": row.status,
            "started_at": row.started_at.isoformat() if row.started_at else None,
            "finished_at": row.finished_at.isoformat() if row.finished_at else None,
            "total_students": row.total_students,
            "already_marked": row.already_marked,
            "auto_absent_marked": row.auto_absent_marked,
            "duplicate_skipped": row.duplicate_skipped,
            "excel_synced": row.excel_synced,
            "attempt_count": row.attempt_count,
            "duration_ms": row.duration_ms,
            "error_message": row.error_message,
        }
        for row in rows
    ]
    return success(data={"items": data, "count": len(data)}, message="Scheduler executions retrieved successfully")


@router.get("/automation/summary")
def scheduler_summary(
    last_n: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
):
    logger.info("event=scheduler_summary_request last_n=%s", last_n)
    summary = auto_absent_service.get_scheduler_summary(db, last_n=last_n)
    return success(data=summary, message="Scheduler summary retrieved successfully")


@router.post("/reports/email/monthly")
def send_monthly_report_email(
    year: int = Query(..., ge=2000, le=2100),
    month: int = Query(..., ge=1, le=12),
    recipient_group: str = Query("admin"),
    department: str | None = None,
    student_id: int | None = Query(default=None, gt=0),
    force_send: bool = Query(False),
    db: Session = Depends(get_db),
):
    logger.info(
        "event=report_email_monthly_request year=%s month=%s recipient_group=%s department=%s student_id=%s force_send=%s",
        year,
        month,
        recipient_group,
        department,
        student_id,
        force_send,
    )
    data = email_service.send_monthly_report_email(
        db,
        year=year,
        month=month,
        recipient_group=recipient_group,
        department=department,
        student_id=student_id,
        force_send=force_send,
    )
    return success(data=data, message="Monthly report email sent successfully")


@router.post("/reports/email/daily")
def send_daily_report_email(
    target_date: date = Query(...),
    recipient_group: str = Query("admin"),
    force_send: bool = Query(False),
    db: Session = Depends(get_db),
):
    logger.info(
        "event=report_email_daily_request date=%s recipient_group=%s force_send=%s",
        target_date,
        recipient_group,
        force_send,
    )
    data = email_service.send_daily_report_email(
        db,
        target_date=target_date,
        recipient_group=recipient_group,
        force_send=force_send,
    )
    return success(data=data, message="Daily report email sent successfully")


@router.get("/reports/email/deliveries")
def list_email_deliveries(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    logger.info("event=email_deliveries_list_request limit=%s", limit)
    rows = email_service.list_email_deliveries(db, limit=limit)
    data = [
        {
            "id": row.id,
            "report_type": row.report_type,
            "report_date": row.report_date.isoformat(),
            "recipient_group": row.recipient_group,
            "report_label": row.report_label,
            "status": row.status,
            "attempts": row.attempts,
            "recipients_count": row.recipients_count,
            "attachment_name": row.attachment_name,
            "duration_ms": row.duration_ms,
            "error_message": row.error_message,
            "started_at": row.started_at.isoformat() if row.started_at else None,
            "finished_at": row.finished_at.isoformat() if row.finished_at else None,
        }
        for row in rows
    ]
    return success(data={"items": data, "count": len(data)}, message="Email delivery history retrieved successfully")


@router.get("/reports/email/summary")
def email_delivery_summary(
    last_n: int = Query(50, ge=1, le=365),
    db: Session = Depends(get_db),
):
    logger.info("event=email_delivery_summary_request last_n=%s", last_n)
    summary = email_service.get_email_delivery_summary(db, last_n=last_n)
    return success(data=summary, message="Email delivery summary retrieved successfully")


@router.get("/{attendance_id}")
def get_attendance(attendance_id: int, db: Session = Depends(get_db)):
    logger.info("event=attendance_get_request attendance_id=%s", attendance_id)
    record = attendance_service.get_attendance_by_id(db, attendance_id)
    return success(data=_serialize_record(record), message="Attendance record retrieved successfully")
