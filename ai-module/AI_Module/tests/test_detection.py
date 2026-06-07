import cv2
import time
from ai_module.utils import CameraHandler, FrameUtils, FaceDetector, get_logger
from ai_module.config import CAMERA_ID, FACE_DETECTION_MODEL, FRAME_RESIZE_SCALE

def run_detection_test():
    logger = get_logger("DetectionTest")
    logger.info("Starting Face Detection Test...")

    try:
        # Initialize Camera and Detector
        cam = CameraHandler(camera_id=CAMERA_ID)
        detector = FaceDetector(model=FACE_DETECTION_MODEL, scale=FRAME_RESIZE_SCALE)
        
        prev_time = 0
        logger.info("Detection system active. Press 'ESC' to exit.")

        while True:
            ret, frame = cam.get_frame()
            if not ret:
                break

            # Process Detection
            face_locations = detector.detect_faces(frame)

            # Draw Boxes for each face
            if face_locations:
                for i, (top, right, bottom, left) in enumerate(face_locations):
                    label = f"Student {i+1}"
                    FrameUtils.draw_face_box(frame, top, right, bottom, left, label=label)
                
                status_text = f"Faces Detected: {len(face_locations)}"
                status_color = (0, 255, 0)
            else:
                status_text = "No Face Detected"
                status_color = (0, 0, 255)

            # Performance Metrics
            curr_time = time.time()
            fps = 1 / (curr_time - prev_time) if (curr_time - prev_time) > 0 else 0
            prev_time = curr_time

            # UI Overlays
            FrameUtils.add_text_overlay(frame, f"FPS: {int(fps)}", position=(10, 30))
            FrameUtils.add_text_overlay(frame, status_text, position=(10, 60), color=status_color)
            FrameUtils.add_text_overlay(frame, "Mode: Detection Only", position=(10, 450), color=(255, 255, 255))

            # Show Result
            cam.show_frame("Face Detection Test", frame)

            # Exit logic
            if cv2.waitKey(1) & 0xFF == 27:
                logger.info("Exit command received.")
                break

    except Exception as e:
        logger.error(f"Detection test failed: {str(e)}")
    
    finally:
        if 'cam' in locals():
            cam.cleanup()
        logger.info("Detection test completed.")

if __name__ == "__main__":
    run_detection_test()
