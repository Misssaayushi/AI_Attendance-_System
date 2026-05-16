import unittest
from unittest.mock import MagicMock, patch

import requests

from ai_module.api_service import AttendanceAPIService
from ai_module.utils import AttendanceManager


class MockHTTPResponse:
    def __init__(self, status_code=200, body=None):
        self.status_code = status_code
        self._body = body if body is not None else {}

    def json(self):
        return self._body


class TestAttendanceAPIService(unittest.TestCase):
    def setUp(self):
        self.service = AttendanceAPIService(
            verify_url="http://127.0.0.1:8000/api/v1/attendance/verify",
            timeout_seconds=0.1,
            retry_count=1,
            retry_delay_seconds=0.0,
            mock_mode=False,
            mock_force_failure=False,
            mock_response_delay_seconds=0.0,
        )

    def test_payload_creation_has_required_fields(self):
        payload = self.service.build_attendance_payload(
            student_id="1",
            name="1_Aayushi",
            confidence=92.5,
        )
        self.assertEqual(payload["student_id"], "1")
        self.assertEqual(payload["name"], "1_Aayushi")
        self.assertEqual(payload["status"], "Present")
        self.assertIsInstance(payload["confidence"], float)
        self.assertIn("T", payload["timestamp"])

    def test_mock_success_mode(self):
        service = AttendanceAPIService(
            mock_mode=True,
            mock_force_failure=False,
            mock_response_delay_seconds=0.0,
        )
        response = service.send_verified_attendance("1", "1_Aayushi", 90.0)
        self.assertTrue(response.success)
        self.assertTrue(response.mocked)
        self.assertEqual(response.status_code, 200)

    def test_mock_failure_mode(self):
        service = AttendanceAPIService(
            mock_mode=True,
            mock_force_failure=True,
            mock_response_delay_seconds=0.0,
        )
        response = service.send_verified_attendance("1", "1_Aayushi", 90.0)
        self.assertFalse(response.success)
        self.assertTrue(response.mocked)
        self.assertEqual(response.status_code, 503)

    @patch("ai_module.api_service.requests.post")
    def test_http_success_200(self, mock_post):
        mock_post.return_value = MockHTTPResponse(200, {"message": "Attendance Logged"})
        response = self.service.send_verified_attendance("1", "1_Aayushi", 90.0)
        self.assertTrue(response.success)
        self.assertFalse(response.mocked)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.message, "Attendance Logged")

    @patch("ai_module.api_service.requests.post")
    def test_http_success_201(self, mock_post):
        mock_post.return_value = MockHTTPResponse(201, {"message": "Created"})
        response = self.service.send_verified_attendance("1", "1_Aayushi", 90.0)
        self.assertTrue(response.success)
        self.assertEqual(response.status_code, 201)

    @patch("ai_module.api_service.requests.post")
    def test_http_failure_500(self, mock_post):
        mock_post.return_value = MockHTTPResponse(500, {"message": "Server Error"})
        response = self.service.send_verified_attendance("1", "1_Aayushi", 90.0)
        self.assertFalse(response.success)
        self.assertEqual(response.status_code, 500)

    @patch("ai_module.api_service.requests.post")
    def test_http_connection_error_returns_safe_failure(self, mock_post):
        mock_post.side_effect = requests.exceptions.ConnectionError("Connection refused")
        response = self.service.send_verified_attendance("1", "1_Aayushi", 90.0)
        self.assertFalse(response.success)
        self.assertIsNone(response.status_code)
        self.assertIsNotNone(response.error)

    @patch("ai_module.api_service.requests.post")
    def test_http_timeout_uses_retries(self, mock_post):
        mock_post.side_effect = requests.exceptions.Timeout("Request timed out")
        response = self.service.send_verified_attendance("1", "1_Aayushi", 90.0)
        self.assertFalse(response.success)
        self.assertEqual(mock_post.call_count, 2)

    def test_invalid_payload_rejected_in_mock_mode(self):
        service = AttendanceAPIService(
            mock_mode=True,
            mock_force_failure=False,
            mock_response_delay_seconds=0.0,
        )
        bad_payload = {
            "student_id": "",
            "name": "Aayushi",
            "confidence": 90.0,
            "timestamp": "",
            "status": "Present",
        }
        response = service.send_payload(bad_payload)  # type: ignore[arg-type]
        self.assertFalse(response.success)
        self.assertEqual(response.status_code, 400)


class TestRecognitionIntegrationBehavior(unittest.TestCase):
    def test_cooldown_prevents_duplicate_transmissions(self):
        manager = AttendanceManager(cooldown_minutes=30, min_confidence=80, stability_frames=1)
        api_service = MagicMock()
        student_id = "1"
        name = "1_Aayushi"

        for _ in range(3):
            verified, _ = manager.verify_attendance(student_id, name, 92.0)
            if verified and name != "Unknown Person":
                api_service.send_verified_attendance(student_id, name, 92.0)

        self.assertEqual(api_service.send_verified_attendance.call_count, 1)

    def test_low_confidence_never_triggers_transmission(self):
        manager = AttendanceManager(cooldown_minutes=30, min_confidence=80, stability_frames=1)
        api_service = MagicMock()
        verified, _ = manager.verify_attendance("2", "2_Student", 60.0)
        if verified:
            api_service.send_verified_attendance("2", "2_Student", 60.0)
        self.assertFalse(verified)
        self.assertEqual(api_service.send_verified_attendance.call_count, 0)


if __name__ == "__main__":
    unittest.main()
