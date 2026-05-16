import cv2
import time
from ai_module.api_service import AttendanceAPIService
from ai_module.utils import CameraHandler, FaceDetector, EncodingManager, FaceRecognizer, AttendanceManager, FrameUtils, get_logger
from ai_module.config import (
    CAMERA_ID, FACE_DETECTION_MODEL, FRAME_RESIZE_SCALE,
    ENCODING_FILE, RECOGNITION_TOLERANCE, RECOGNITION_PROCESS_INTERVAL,
    UNKNOWN_LABEL, API_FEEDBACK_DISPLAY_SECONDS
)


def _resolve_api_feedback(api_response):
    if api_response.success:
        if api_response.mocked:
            return api_response.message, (0, 255, 255)
        return api_response.message, (0, 255, 0)

    error_text = (api_response.error or "").lower()
    if "timed out" in error_text or "timeout" in error_text:
        return "Backend Timeout", (0, 0, 255)
    if "failed to establish a new connection" in error_text or "connection" in error_text:
        return "Backend Offline", (0, 0, 255)
    return api_response.message or "Server Error", (0, 0, 255)


def _resolve_verification_color(name, verified):
    if name == UNKNOWN_LABEL:
        return (0, 0, 255)
    if verified:
        return (0, 255, 0)
    return (0, 255, 255)


def _short_verification_status(status_text):
    lower_text = status_text.lower()
    if "verified:" in lower_text:
        return "Verified"
    if "cooldown" in lower_text:
        return "Cooldown"
    if "stability" in lower_text:
        return "Stability"
    if "unknown" in lower_text:
        return "Unknown"
    if "low confidence" in lower_text:
        return "LowConf"
    return "Pending"


def _short_api_status(api_text):
    lower_text = api_text.lower()
    if "logged" in lower_text or "success" in lower_text:
        return "Logged"
    if "timeout" in lower_text:
        return "Timeout"
    if "offline" in lower_text or "connection" in lower_text:
        return "Offline"
    if "error" in lower_text or "failure" in lower_text:
        return "Error"
    return "Pending"


def _draw_status_legend(frame):
    height, width = frame.shape[:2]
    legend_x = max(10, width - 330)
    legend_y = 10
    legend_w = 315
    legend_h = 125

    cv2.rectangle(frame, (legend_x, legend_y), (legend_x + legend_w, legend_y + legend_h), (35, 35, 35), cv2.FILLED)
    cv2.rectangle(frame, (legend_x, legend_y), (legend_x + legend_w, legend_y + legend_h), (255, 255, 255), 1)

    cv2.putText(frame, "Status Legend", (legend_x + 10, legend_y + 22), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)
    cv2.putText(frame, "V = verification state", (legend_x + 10, legend_y + 45), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (220, 220, 220), 1)
    cv2.putText(frame, "API = backend transmission", (legend_x + 10, legend_y + 64), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (220, 220, 220), 1)

    cv2.rectangle(frame, (legend_x + 10, legend_y + 80), (legend_x + 24, legend_y + 94), (0, 255, 0), cv2.FILLED)
    cv2.putText(frame, "Green: Verified / Logged", (legend_x + 30, legend_y + 92), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)

    cv2.rectangle(frame, (legend_x + 10, legend_y + 100), (legend_x + 24, legend_y + 114), (0, 255, 255), cv2.FILLED)
    cv2.putText(frame, "Yellow: Pending / Cooldown", (legend_x + 30, legend_y + 112), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)

    cv2.rectangle(frame, (legend_x + 180, legend_y + 100), (legend_x + 194, legend_y + 114), (0, 0, 255), cv2.FILLED)
    cv2.putText(frame, "Red: Unknown / Error", (legend_x + 200, legend_y + 112), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)


def start_recognition():
    logger = get_logger("RealTimeRecognition")
    logger.info("Initializing Face Recognition System...")

    try:
        # 1. Initialize Components
        cam = CameraHandler(camera_id=CAMERA_ID)
        detector = FaceDetector(model=FACE_DETECTION_MODEL, scale=FRAME_RESIZE_SCALE)
        
        # Load encodings and managers
        manager = EncodingManager(encoding_file=ENCODING_FILE)
        recognizer = FaceRecognizer(encoding_manager=manager, tolerance=RECOGNITION_TOLERANCE)
        attendance_manager = AttendanceManager()
        api_service = AttendanceAPIService()

        process_this_frame = True
        frame_count = 0
        recent_api_feedback = {}
        
        # Recognition results storage
        face_locations = []
        face_names = []
        face_confidences = []
        face_statuses = []

        logger.info("Recognition system active. Press 'ESC' to exit.")

        while True:
            ret, frame = cam.get_frame()
            if not ret:
                break

            # 2. Process every Nth frame for performance
            if frame_count % RECOGNITION_PROCESS_INTERVAL == 0:
                # Detect Faces
                new_face_locations = detector.detect_faces(frame)
                
                # If a face leaves the frame, reset its stability (optional but professional)
                # For simplicity, we refresh the results every interval
                
                face_locations = new_face_locations
                face_names = []
                face_confidences = []
                face_statuses = []

                for face_loc in face_locations:
                    # Stage 1: Identify Face
                    name, confidence = recognizer.identify(frame, face_loc)
                    face_names.append(name)
                    face_confidences.append(confidence)

                    # Stage 2: Verify Attendance (Cooldown, Stability, Thresholds)
                    # We extract the ID from the name (e.g., "1_Aayushi" -> "1")
                    student_id = name.split("_")[0] if "_" in name else name
                    
                    verified, verification_status = attendance_manager.verify_attendance(student_id, name, confidence)
                    verification_color = _resolve_verification_color(name, verified)
                    api_status = "NotSent"
                    api_color = (160, 160, 160)

                    now = time.time()
                    cached_feedback = recent_api_feedback.get(student_id)
                    if cached_feedback and cached_feedback["expires_at"] > now:
                        api_status = cached_feedback["message"]
                        api_color = cached_feedback["color"]

                    if verified and name != UNKNOWN_LABEL:
                        api_response = api_service.send_verified_attendance(
                            student_id=student_id,
                            name=name,
                            confidence=confidence,
                        )
                        api_status, api_color = _resolve_api_feedback(api_response)
                        recent_api_feedback[student_id] = {
                            "message": api_status,
                            "color": api_color,
                            "expires_at": now + API_FEEDBACK_DISPLAY_SECONDS,
                        }

                    final_color = api_color if api_status != "NotSent" else verification_color
                    face_statuses.append((verification_status, api_status, final_color))

            frame_count += 1

            # 3. Visualization
            for (top, right, bottom, left), name, conf, (verification_status, api_status, color) in zip(face_locations, face_names, face_confidences, face_statuses):
                verification_badge = _short_verification_status(verification_status)
                api_badge = _short_api_status(api_status) if api_status != "NotSent" else "Skip"
                label = f"{name} | V:{verification_badge} | API:{api_badge}"
                FrameUtils.draw_face_box(frame, top, right, bottom, left, label=label, color=color)

            # UI Overlays
            FrameUtils.add_text_overlay(frame, "System: ATTENDANCE VERIFICATION", position=(10, 30))
            FrameUtils.add_text_overlay(frame, f"Faces in View: {len(face_locations)}", position=(10, 60))
            _draw_status_legend(frame)
            FrameUtils.add_text_overlay(frame, "Press ESC to Quit", position=(10, 450), color=(255, 255, 255))

            cam.show_frame("AI Attendance Recognition", frame)

            if cv2.waitKey(1) & 0xFF == 27:
                logger.info("Exit command received.")
                break

    except Exception as e:
        logger.error(f"System Error: {str(e)}")
    
    finally:
        if 'cam' in locals():
            cam.cleanup()

if __name__ == "__main__":
    start_recognition()
