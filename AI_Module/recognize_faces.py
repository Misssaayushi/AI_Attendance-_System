import cv2
import time
from ai_module.utils import CameraHandler, FaceDetector, EncodingManager, FaceRecognizer, FrameUtils, get_logger
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
        
        # Load encodings into memory
        manager = EncodingManager(encoding_file=ENCODING_FILE)
        recognizer = FaceRecognizer(encoding_manager=manager, tolerance=RECOGNITION_TOLERANCE)

        process_this_frame = True
        frame_count = 0
        
        # Recognition results storage for persistence between frames
        face_locations = []
        face_names = []
        face_confidences = []

        logger.info("Recognition system active. Press 'ESC' to exit.")

        while True:
            ret, frame = cam.get_frame()
            if not ret:
                break

            # 2. Process every Nth frame for performance
            if frame_count % RECOGNITION_PROCESS_INTERVAL == 0:
                # Detect Faces
                face_locations = detector.detect_faces(frame)
                
                face_names = []
                face_confidences = []

                for face_loc in face_locations:
                    # Identify Face
                    name, confidence = recognizer.identify(frame, face_loc)
                    face_names.append(name)
                    face_confidences.append(confidence)

            frame_count += 1

            # 3. Visualization
            for (top, right, bottom, left), name, conf in zip(face_locations, face_names, face_confidences):
                # Professional label with confidence
                label = f"{name} ({conf:.1f}%)" if name != UNKNOWN_LABEL else name
                FrameUtils.draw_face_box(frame, top, right, bottom, left, label=label)

            # UI Overlays
            FrameUtils.add_text_overlay(frame, "System: RECOGNITION MODE", position=(10, 30))
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
