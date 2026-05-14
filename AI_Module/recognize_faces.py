import cv2
import time
from ai_module.utils import CameraHandler, FaceDetector, EncodingManager, FaceRecognizer, AttendanceManager, FrameUtils, get_logger
from ai_module.config import (
    CAMERA_ID, FACE_DETECTION_MODEL, FRAME_RESIZE_SCALE,
    ENCODING_FILE, RECOGNITION_TOLERANCE, RECOGNITION_PROCESS_INTERVAL,
    UNKNOWN_LABEL
)

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

        process_this_frame = True
        frame_count = 0
        
        # Recognition results storage
        face_locations = []
        face_names = []
        face_confidences = []
        face_statuses = []  # Added for verification status

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
                    
                    verified, status_msg = attendance_manager.verify_attendance(student_id, name, confidence)
                    face_statuses.append((verified, status_msg))

            frame_count += 1

            # 3. Visualization
            for (top, right, bottom, left), name, conf, (verified, status) in zip(face_locations, face_names, face_confidences, face_statuses):
                # Determine Color: Green = Verified, Yellow = Process, Red = Unknown
                if name == UNKNOWN_LABEL:
                    color = (0, 0, 255) # Red
                elif verified:
                    color = (0, 255, 0) # Green
                else:
                    color = (0, 255, 255) # Yellow

                label = f"{name} | {status}"
                FrameUtils.draw_face_box(frame, top, right, bottom, left, label=label, color=color)

            # UI Overlays
            FrameUtils.add_text_overlay(frame, "System: ATTENDANCE VERIFICATION", position=(10, 30))
            FrameUtils.add_text_overlay(frame, f"Faces in View: {len(face_locations)}", position=(10, 60))
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
