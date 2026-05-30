import cv2
import time
import sys
from pathlib import Path

try:
    from ai_module.api_service import AttendanceAPIService
    from ai_module.utils import (
        CameraHandler,
        FaceDetector,
        EncodingManager,
        FaceRecognizer,
        AttendanceManager,
        FrameUtils,
        get_logger,
    )
    from ai_module.config import (
        CAMERA_ID,
        FACE_DETECTION_MODEL,
        FRAME_RESIZE_SCALE,
        ENCODING_FILE,
        RECOGNITION_TOLERANCE,
        UNKNOWN_LABEL,
        API_FEEDBACK_DISPLAY_SECONDS,
        ENABLE_FPS_OVERLAY,
        DEBUG_MODE,
        API_FEEDBACK_CLEANUP_INTERVAL,
    )
except ImportError:
    from api_service import AttendanceAPIService
    from utils import (
        CameraHandler,
        FaceDetector,
        EncodingManager,
        FaceRecognizer,
        AttendanceManager,
        FrameUtils,
        get_logger,
    )
    from config import (
        CAMERA_ID,
        FACE_DETECTION_MODEL,
        FRAME_RESIZE_SCALE,
        ENCODING_FILE,
        RECOGNITION_TOLERANCE,
        UNKNOWN_LABEL,
        API_FEEDBACK_DISPLAY_SECONDS,
        ENABLE_FPS_OVERLAY,
        DEBUG_MODE,
        API_FEEDBACK_CLEANUP_INTERVAL,
    )

try:
    from ai_module.optimization import (
        EncodingCache,
        PerformanceTracker,
        FrameOptimizer,
        APIDispatcher,
    )
except ImportError:
    try:
        from optimization import (
            EncodingCache,
            PerformanceTracker,
            FrameOptimizer,
            APIDispatcher,
        )
    except ImportError:
        sys.path.append(str(Path(__file__).resolve().parent))
        from optimization import (
            EncodingCache,
            PerformanceTracker,
            FrameOptimizer,
            APIDispatcher,
        )


def _resolve_api_feedback(api_response):
    if api_response.success:
        if api_response.mocked:
            return api_response.message, (0, 255, 255)
        return api_response.message, (0, 255, 0)

    error_text = (api_response.error or "").lower()
    if "timed out" in error_text or "timeout" in error_text:
        return "Backend Timeout", (0, 0, 255)
    if (
        "failed to establish a new connection" in error_text
        or "connection" in error_text
    ):
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

    cv2.rectangle(
        frame,
        (legend_x, legend_y),
        (legend_x + legend_w, legend_y + legend_h),
        (35, 35, 35),
        cv2.FILLED,
    )
    cv2.rectangle(
        frame,
        (legend_x, legend_y),
        (legend_x + legend_w, legend_y + legend_h),
        (255, 255, 255),
        1,
    )

    cv2.putText(
        frame,
        "Status Legend",
        (legend_x + 10, legend_y + 22),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        1,
    )
    cv2.putText(
        frame,
        "V = verification state",
        (legend_x + 10, legend_y + 45),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (220, 220, 220),
        1,
    )
    cv2.putText(
        frame,
        "API = backend transmission",
        (legend_x + 10, legend_y + 64),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (220, 220, 220),
        1,
    )

    cv2.rectangle(
        frame,
        (legend_x + 10, legend_y + 80),
        (legend_x + 24, legend_y + 94),
        (0, 255, 0),
        cv2.FILLED,
    )
    cv2.putText(
        frame,
        "Green: Verified / Logged",
        (legend_x + 30, legend_y + 92),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (255, 255, 255),
        1,
    )

    cv2.rectangle(
        frame,
        (legend_x + 10, legend_y + 100),
        (legend_x + 24, legend_y + 114),
        (0, 255, 255),
        cv2.FILLED,
    )
    cv2.putText(
        frame,
        "Yellow: Pending / Cooldown",
        (legend_x + 30, legend_y + 112),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (255, 255, 255),
        1,
    )

    cv2.rectangle(
        frame,
        (legend_x + 180, legend_y + 100),
        (legend_x + 194, legend_y + 114),
        (0, 0, 255),
        cv2.FILLED,
    )
    cv2.putText(
        frame,
        "Red: Unknown / Error",
        (legend_x + 200, legend_y + 112),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (255, 255, 255),
        1,
    )


def start_recognition():
    logger = get_logger("RealTimeRecognition")
    logger.info("Initializing Optimized Face Recognition System (Phase 7)...")

    try:
        # 1. Initialize Components
        cam = CameraHandler(camera_id=CAMERA_ID)
        detector = FaceDetector(
            model=FACE_DETECTION_MODEL, scale=FRAME_RESIZE_SCALE
        )

        # Load optimized EncodingCache singleton eager load
        cache = EncodingCache.get_instance()
        cache.load(ENCODING_FILE)

        # Retain backward compatibility manager, which queries the cache dynamically  # noqa: E501
        manager = EncodingManager(encoding_file=ENCODING_FILE)
        recognizer = FaceRecognizer(
            encoding_manager=manager, tolerance=RECOGNITION_TOLERANCE
        )

        frame_optimizer = FrameOptimizer()
        perf_tracker = PerformanceTracker()
        api_dispatcher = APIDispatcher()

        attendance_manager = AttendanceManager()
        api_service = AttendanceAPIService()

        frame_count = 0
        retry_count = 0
        recent_api_feedback = {}

        # Recognition results storage
        face_locations = []
        face_names = []
        face_confidences = []
        face_statuses = []

        logger.info("Recognition system active. Press 'ESC' to exit.")

        while True:
            perf_tracker.tick()

            ret, frame = cam.get_frame()
            if not ret:
                retry_count += 1
                if retry_count >= 3:
                    logger.error("Webcam failed after 3 retries. Exiting.")
                    break
                time.sleep(0.05)
                continue
            retry_count = 0

            # 2. Get current adaptive processing interval recommendations
            interval = perf_tracker.get_recommended_interval()

            if frame_count % interval == 0:
                # Prepare/reuse RGB frame and get locations
                rgb_frame = frame_optimizer.prepare_frame(frame)

                # Step 6.2: We call detect_faces and fetch scaled face locations  # noqa: E501
                face_locations = detector.detect_faces(frame)

                face_names = []
                face_confidences = []
                face_statuses = []

                # Record time spend on active AI processing
                ai_start_time = time.perf_counter()

                for face_loc in face_locations:
                    # Stage 1: Optimized identify using pre-cropped face encoding  # noqa: E501
                    # Reduce compute from ~307K pixels to ~36K pixels
                    encoding, success = frame_optimizer.generate_encoding(
                        rgb_frame, face_loc
                    )

                    if encoding is not None:
                        name, confidence = recognizer.identify_optimized(
                            encoding
                        )
                    else:
                        name, confidence = UNKNOWN_LABEL, 0.0

                    face_names.append(name)
                    face_confidences.append(confidence)

                    # Stage 2: Verify Attendance (Cooldown, Stability, Thresholds)  # noqa: E501
                    student_id = name.split("_")[0] if "_" in name else name

                    verified, verification_status = (
                        attendance_manager.verify_attendance(
                            student_id, name, confidence
                        )
                    )
                    verification_color = _resolve_verification_color(
                        name, verified
                    )

                    # API Status resolution
                    api_status = "NotSent"
                    api_color = (160, 160, 160)

                    # Non-blocking async API dispatch
                    if verified and name != UNKNOWN_LABEL:
                        api_dispatcher.dispatch(
                            api_service, student_id, name, confidence
                        )

                    # Check for completed async dispatcher results or pending states  # noqa: E501
                    if api_dispatcher.is_pending(student_id):
                        api_status = "Pending..."
                        api_color = (0, 255, 255)  # Yellow
                    else:
                        # Check if completed result exists
                        completed, api_response = api_dispatcher.get_result(
                            student_id
                        )
                        if completed:
                            api_status, api_color = _resolve_api_feedback(
                                api_response
                            )
                            # Cache in local feedback dictionary for display duration tracking  # noqa: E501
                            recent_api_feedback[student_id] = {
                                "message": api_status,
                                "color": api_color,
                                "expires_at": time.time()
                                + API_FEEDBACK_DISPLAY_SECONDS,
                            }
                        else:
                            # Fallback check on previously cached local feedback  # noqa: E501
                            now = time.time()
                            cached_feedback = recent_api_feedback.get(
                                student_id
                            )
                            if (
                                cached_feedback
                                and cached_feedback["expires_at"] > now
                            ):
                                api_status = cached_feedback["message"]
                                api_color = cached_feedback["color"]

                    final_color = (
                        api_color
                        if api_status != "NotSent"
                        else verification_color
                    )
                    face_statuses.append(
                        (verification_status, api_status, final_color)
                    )

                # Track AI duration
                ai_duration_ms = (time.perf_counter() - ai_start_time) * 1000.0
                perf_tracker.record_processing_time(ai_duration_ms)

            # 3. Visualization and Overlay Draw
            for (
                (top, right, bottom, left),
                name,
                conf,
                (verification_status, api_status, color),
            ) in zip(
                face_locations, face_names, face_confidences, face_statuses
            ):
                verification_badge = _short_verification_status(
                    verification_status
                )
                api_badge = (
                    _short_api_status(api_status)
                    if api_status != "NotSent"
                    else "Skip"
                )
                label = f"{name} | V:{verification_badge} | API:{api_badge}"
                FrameUtils.draw_face_box(
                    frame, top, right, bottom, left, label=label, color=color
                )

            # Dynamic performance tracking info overlay
            if ENABLE_FPS_OVERLAY and DEBUG_MODE:
                FrameUtils.add_text_overlay(
                    frame,
                    f"System: {perf_tracker.get_status_string()}",
                    position=(10, 30),
                )
            else:
                FrameUtils.add_text_overlay(
                    frame, "System: ATTENDANCE VERIFICATION", position=(10, 30)
                )

            FrameUtils.add_text_overlay(
                frame,
                f"Faces in View: {len(face_locations)}",
                position=(10, 60),
            )
            _draw_status_legend(frame)
            FrameUtils.add_text_overlay(
                frame,
                "Press ESC to Quit",
                position=(10, 450),
                color=(255, 255, 255),
            )

            cam.show_frame("AI Attendance Recognition", frame)

            # Periodic Memory and Cache Cleanup
            if frame_count % API_FEEDBACK_CLEANUP_INTERVAL == 0:
                # Clean expired local API feedback dictionary
                now = time.time()
                expired_keys = [
                    k
                    for k, v in recent_api_feedback.items()
                    if v["expires_at"] < now
                ]
                for k in expired_keys:
                    del recent_api_feedback[k]

                # Clean expired dispatcher results history
                api_dispatcher.collect_expired()

                # Transparent reload check on known encodings disk changes
                cache.reload_if_changed()

            # Prevent integer overflow in frame_count
            frame_count = (frame_count + 1) % 1_000_000

            if cv2.waitKey(1) & 0xFF == 27:
                logger.info("Exit command received.")
                break

    except Exception as e:
        logger.error(f"System Error: {str(e)}")

    finally:
        # Step 7.9: Dispatcher and Camera resource cleanups in finally block
        if "api_dispatcher" in locals():
            api_dispatcher.cleanup(timeout=2.0)
        if "cam" in locals():
            cam.cleanup()


if __name__ == "__main__":
    start_recognition()
