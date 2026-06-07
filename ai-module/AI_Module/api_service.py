from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional, TypedDict

import requests

try:
    from ai_module.config import (
        API_ERROR_MESSAGE,
        API_MOCK_FORCE_FAILURE,
        API_MOCK_MODE,
        API_MOCK_RESPONSE_DELAY_SECONDS,
        API_RETRY_COUNT,
        API_RETRY_DELAY_SECONDS,
        API_SUCCESS_MESSAGE,
        API_TIMEOUT_SECONDS,
        ATTENDANCE_VERIFY_URL,
        ATTENDANCE_UNRECOGNIZED_URL,
    )
    from ai_module.utils import get_logger
except ImportError:
    from config import (
        API_ERROR_MESSAGE,
        API_MOCK_FORCE_FAILURE,
        API_MOCK_MODE,
        API_MOCK_RESPONSE_DELAY_SECONDS,
        API_RETRY_COUNT,
        API_RETRY_DELAY_SECONDS,
        API_SUCCESS_MESSAGE,
        API_TIMEOUT_SECONDS,
        ATTENDANCE_VERIFY_URL,
        ATTENDANCE_UNRECOGNIZED_URL,
    )
    from utils import get_logger


class AttendancePayload(TypedDict):
    student_id: str
    name: str
    confidence: float
    timestamp: str
    status: str


FAILED_EVENTS_FILE = Path(__file__).parent / "logs" / "failed_events.jsonl"
FAILED_EVENTS_FILE.parent.mkdir(parents=True, exist_ok=True)


@dataclass
class AttendanceAPIResponse:
    success: bool
    message: str
    status_code: Optional[int] = None
    mocked: bool = False
    error: Optional[str] = None


class AttendanceAPIService:
    """
    Handles attendance event transmission from the AI module to backend API.
    """

    def __init__(
        self,
        verify_url: str = ATTENDANCE_VERIFY_URL,
        unrecognized_url: str = ATTENDANCE_UNRECOGNIZED_URL,
        timeout_seconds: float = API_TIMEOUT_SECONDS,
        retry_count: int = API_RETRY_COUNT,
        retry_delay_seconds: float = API_RETRY_DELAY_SECONDS,
        mock_mode: bool = API_MOCK_MODE,
        mock_force_failure: bool = API_MOCK_FORCE_FAILURE,
        mock_response_delay_seconds: float = API_MOCK_RESPONSE_DELAY_SECONDS,
    ) -> None:
        self.verify_url = verify_url
        self.unrecognized_url = unrecognized_url
        self.timeout_seconds = timeout_seconds
        self.retry_count = max(0, retry_count)
        self.retry_delay_seconds = max(0.0, retry_delay_seconds)
        self.mock_mode = mock_mode
        self.mock_force_failure = mock_force_failure
        self.mock_response_delay_seconds = max(0.0, mock_response_delay_seconds)
        self.logger = get_logger("API_Connector")
        self.api_key = os.getenv("AI_MODULE_API_KEY", "ai-module-secret-key")

    def build_attendance_payload(
        self,
        student_id: str,
        name: str,
        confidence: float,
        status: str = "Present",
        timestamp: Optional[datetime] = None,
    ) -> AttendancePayload:
        """
        Build AI-owned attendance payload with timestamp and confidence.
        """
        event_time = timestamp or datetime.now(timezone.utc)
        return AttendancePayload(
            student_id=str(student_id),
            name=str(name),
            confidence=float(confidence),
            timestamp=event_time.isoformat(),
            status=str(status),
        )

    def send_verified_attendance(
        self,
        student_id: str,
        name: str,
        confidence: float,
        status: str = "Present",
        timestamp: Optional[datetime] = None,
    ) -> AttendanceAPIResponse:
        """
        Build and transmit an attendance payload.
        """
        payload = self.build_attendance_payload(
            student_id=student_id,
            name=name,
            confidence=confidence,
            status=status,
            timestamp=timestamp,
        )
        return self.send_payload(payload)

    def send_unrecognized_event(self) -> AttendanceAPIResponse:
        """
        Send an unrecognized face event to the backend.
        """
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "confidence": 0.0
        }
        
        if self.mock_mode:
            return self._send_mock({"student_id": "unknown", "name": "unknown", "confidence": 0.0, "status": "unknown", "timestamp": payload["timestamp"]})
            
        attempts = self.retry_count + 1
        last_error = None
        
        for attempt in range(1, attempts + 1):
            try:
                response = requests.post(
                    self.unrecognized_url,
                    json=payload,
                    timeout=self.timeout_seconds,
                    headers={"X-API-Key": self.api_key},
                )
                return self._build_response_from_http(response)
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as exc:
                last_error = str(exc)
                if attempt < attempts and self.retry_delay_seconds > 0:
                    time.sleep(self.retry_delay_seconds)
            except requests.exceptions.RequestException as exc:
                last_error = str(exc)
                return AttendanceAPIResponse(
                    success=False,
                    message=API_ERROR_MESSAGE,
                    status_code=None,
                    mocked=False,
                    error=last_error,
                )

        return AttendanceAPIResponse(
            success=False,
            message=API_ERROR_MESSAGE,
            status_code=None,
            mocked=False,
            error=last_error or "Unknown network error",
        )

    def send_payload(self, payload: AttendancePayload) -> AttendanceAPIResponse:
        """
        Send attendance payload in mock mode or real HTTP mode.
        """
        validation_error = self._validate_payload(payload)
        if validation_error is not None:
            return validation_error

        # Try to replay any previously failed events before sending new one
        self.replay_failed_events()

        if self.mock_mode:
            return self._send_mock(payload)
        return self._send_http(payload)

    def _send_mock(self, payload: AttendancePayload) -> AttendanceAPIResponse:
        if self.mock_response_delay_seconds > 0:
            time.sleep(self.mock_response_delay_seconds)

        if self.mock_force_failure:
            message = "Mock Failure: Backend Rejected Event"
            self.logger.warning("Mock transmission failed for student_id=%s", payload["student_id"])
            return AttendanceAPIResponse(
                success=False,
                message=message,
                status_code=503,
                mocked=True,
                error=message,
            )

        message = "Mock Success: Attendance Logged"
        self.logger.info("Mock transmission succeeded for student_id=%s", payload["student_id"])
        return AttendanceAPIResponse(
            success=True,
            message=message,
            status_code=200,
            mocked=True,
            error=None,
        )

    def _send_http(self, payload: AttendancePayload) -> AttendanceAPIResponse:
        attempts = self.retry_count + 1
        last_error = None

        for attempt in range(1, attempts + 1):
            try:
                response = requests.post(
                    self.verify_url,
                    json=payload,
                    timeout=self.timeout_seconds,
                    headers={"X-API-Key": self.api_key},
                )
                return self._build_response_from_http(response)
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as exc:
                last_error = str(exc)
                self.logger.warning(
                    "Attendance transmission attempt %s/%s failed: %s",
                    attempt,
                    attempts,
                    last_error,
                )
                if attempt < attempts and self.retry_delay_seconds > 0:
                    time.sleep(self.retry_delay_seconds)
            except requests.exceptions.RequestException as exc:
                last_error = str(exc)
                self.logger.error("Attendance request error: %s", last_error)
                self._queue_failed_event(payload)
                return AttendanceAPIResponse(
                    success=False,
                    message=API_ERROR_MESSAGE,
                    status_code=None,
                    mocked=False,
                    error=last_error,
                )

        self._queue_failed_event(payload)
        return AttendanceAPIResponse(
            success=False,
            message=API_ERROR_MESSAGE,
            status_code=None,
            mocked=False,
            error=last_error or "Unknown network error",
        )

    def _validate_payload(self, payload: AttendancePayload) -> Optional[AttendanceAPIResponse]:
        student_id = str(payload.get("student_id", "")).strip()
        name = str(payload.get("name", "")).strip()
        status = str(payload.get("status", "")).strip()
        timestamp = str(payload.get("timestamp", "")).strip()
        confidence_value = payload.get("confidence")

        if not student_id:
            return self._invalid_payload_response("Missing student_id")
        if not name:
            return self._invalid_payload_response("Missing name")
        if not status:
            return self._invalid_payload_response("Missing status")
        if not timestamp:
            return self._invalid_payload_response("Missing timestamp")

        try:
            float(confidence_value)
        except (TypeError, ValueError):
            return self._invalid_payload_response("Confidence must be numeric")

        if timestamp.endswith("Z"):
            timestamp = timestamp[:-1] + "+00:00"
        try:
            datetime.fromisoformat(timestamp)
        except ValueError:
            return self._invalid_payload_response("Timestamp must be ISO-8601")

        return None

    def _invalid_payload_response(self, reason: str) -> AttendanceAPIResponse:
        self.logger.warning("Payload validation failed: %s", reason)
        return AttendanceAPIResponse(
            success=False,
            message="Invalid attendance payload",
            status_code=400,
            mocked=self.mock_mode,
            error=reason,
        )

    def _build_response_from_http(self, response: requests.Response) -> AttendanceAPIResponse:
        status_code = response.status_code
        body = self._safe_json(response)
        body_message = self._extract_message(body)

        if status_code in (200, 201):
            message = body_message or API_SUCCESS_MESSAGE
            self.logger.info("Attendance logged successfully. status_code=%s", status_code)
            return AttendanceAPIResponse(
                success=True,
                message=message,
                status_code=status_code,
                mocked=False,
                error=None,
            )

        error_message = body_message or API_ERROR_MESSAGE
        self.logger.warning(
            "Attendance transmission rejected. status_code=%s message=%s",
            status_code,
            error_message,
        )
        return AttendanceAPIResponse(
            success=False,
            message=error_message,
            status_code=status_code,
            mocked=False,
            error=error_message,
        )

    @staticmethod
    def _safe_json(response: requests.Response) -> Optional[dict[str, Any]]:
        try:
            data = response.json()
            if isinstance(data, dict):
                return data
            return None
        except ValueError:
            return None

    @staticmethod
    def _extract_message(body: Optional[dict[str, Any]]) -> Optional[str]:
        if not body:
            return None
        for key in ("message", "detail", "status"):
            value = body.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return None

    def _queue_failed_event(self, payload: AttendancePayload) -> None:
        """Store failed event for later replay."""
        try:
            with open(FAILED_EVENTS_FILE, "a") as f:
                f.write(json.dumps(payload) + "\n")
            self.logger.info("Queued failed event for student_id=%s", payload["student_id"])
        except Exception as exc:
            self.logger.error("Failed to queue event: %s", str(exc))

    def replay_failed_events(self) -> int:
        """Attempt to resend previously failed events."""
        if not FAILED_EVENTS_FILE.exists():
            return 0
        
        replayed = 0
        remaining = []
        
        try:
            with open(FAILED_EVENTS_FILE, "r") as f:
                lines = f.readlines()
                
            for line in lines:
                try:
                    payload = json.loads(line.strip())
                    # Skip replay if it fails validation
                    if self._validate_payload(payload) is not None:
                        continue
                        
                    # Send payload directly to avoid infinite recursion
                    if self.mock_mode:
                        result = self._send_mock(payload)
                    else:
                        result = self._send_http_no_queue(payload)
                        
                    if result.success:
                        replayed += 1
                        self.logger.info("Successfully replayed queued event for student_id=%s", payload["student_id"])
                    else:
                        remaining.append(line)
                except Exception:
                    remaining.append(line)
            
            if replayed > 0 or len(remaining) != len(lines):
                with open(FAILED_EVENTS_FILE, "w") as f:
                    f.writelines(remaining)
                    
        except Exception as exc:
            self.logger.error("Failed to replay queued events: %s", str(exc))
            
        return replayed

    def _send_http_no_queue(self, payload: AttendancePayload) -> AttendanceAPIResponse:
        """Helper to send HTTP request without queuing on failure (used during replay)."""
        attempts = self.retry_count + 1
        last_error = None

        for attempt in range(1, attempts + 1):
            try:
                response = requests.post(
                    self.verify_url,
                    json=payload,
                    timeout=self.timeout_seconds,
                    headers={"X-API-Key": self.api_key},
                )
                return self._build_response_from_http(response)
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as exc:
                last_error = str(exc)
                if attempt < attempts and self.retry_delay_seconds > 0:
                    time.sleep(self.retry_delay_seconds)
            except requests.exceptions.RequestException as exc:
                last_error = str(exc)
                return AttendanceAPIResponse(
                    success=False,
                    message=API_ERROR_MESSAGE,
                    status_code=None,
                    mocked=False,
                    error=last_error,
                )

        return AttendanceAPIResponse(
            success=False,
            message=API_ERROR_MESSAGE,
            status_code=None,
            mocked=False,
            error=last_error or "Unknown network error",
        )

