import cv2
import time
from ai_module.utils import CameraHandler, FrameUtils, get_logger
from ai_module.config import CAMERA_ID

def run_test():
    logger = get_logger("TestSystem")
    logger.info("Starting System Test...")

    try:
        # Initialize Camera
        cam = CameraHandler(camera_id=CAMERA_ID)
        
        # FPS calculation variables
        prev_time = 0
        
        logger.info("Webcam started. Press 'ESC' to exit.")

        while True:
            ret, frame = cam.get_frame()
            if not ret:
                break

            # Calculate FPS
            curr_time = time.time()
            fps = 1 / (curr_time - prev_time)
            prev_time = curr_time

            # Add Debug Overlays
            FrameUtils.add_text_overlay(frame, f"FPS: {int(fps)}", position=(10, 30))
            FrameUtils.add_text_overlay(frame, "System: Ready", position=(10, 60))
            FrameUtils.add_text_overlay(frame, "Press ESC to Exit", position=(10, 90), color=(0, 0, 255))

            # Show Frame
            cam.show_frame("AI Attendance System - Test Mode", frame)

            # Exit logic (ESC key)
            if cv2.waitKey(1) & 0xFF == 27:
                logger.info("Exit command received.")
                break

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
    
    finally:
        if 'cam' in locals():
            cam.cleanup()
        logger.info("Test completed cleanly.")

if __name__ == "__main__":
    run_test()
