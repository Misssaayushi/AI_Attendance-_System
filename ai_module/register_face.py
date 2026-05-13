import cv2
import time
import os
from ai_module.utils import CameraHandler, FaceDetector, FaceValidator, FrameUtils, get_logger
from ai_module.config import (
    CAMERA_ID, FACE_DETECTION_MODEL, FRAME_RESIZE_SCALE,
    DATASET_DIR, CAPTURE_SAMPLE_COUNT, CAPTURE_INTERVAL,
    BLUR_THRESHOLD, BRIGHTNESS_MIN, BRIGHTNESS_MAX, MIN_FACE_SIZE,
    IMAGE_QUALITY
)

def register_student():
    logger = get_logger("RegisterFace")
    
    # 1. Get Student Details
    print("\n--- Student Registration ---")
    student_id = input("Enter Student ID (Roll No): ").strip()
    student_name = input("Enter Student Name: ").strip()

    if not student_id or not student_name:
        logger.error("ID and Name are required.")
        return

    # Create folder: dataset/ID_Name
    student_folder = DATASET_DIR / f"{student_id}_{student_name}"
    student_folder.mkdir(parents=True, exist_ok=True)

    # 2. Initialize Hardware & AI
    try:
        cam = CameraHandler(camera_id=CAMERA_ID)
        detector = FaceDetector(model=FACE_DETECTION_MODEL, scale=FRAME_RESIZE_SCALE)
        validator = FaceValidator(
            blur_threshold=BLUR_THRESHOLD,
            brightness_min=BRIGHTNESS_MIN,
            brightness_max=BRIGHTNESS_MAX,
            min_face_size=MIN_FACE_SIZE
        )

        samples_captured = 0
        last_capture_time = 0
        
        logger.info(f"Starting capture for {student_name}. Need {CAPTURE_SAMPLE_COUNT} samples.")

        while samples_captured < CAPTURE_SAMPLE_COUNT:
            ret, frame = cam.get_frame()
            if not ret:
                break

            # Clone frame for UI (don't want detection boxes in saved images)
            display_frame = frame.copy()

            # Detect Faces
            face_locations = detector.detect_faces(frame)
            
            status_message = "No Face Detected"
            status_color = (0, 0, 255)

            if len(face_locations) == 1:
                face_loc = face_locations[0]
                
                # Validate Quality
                is_valid, reason = validator.validate(frame, face_loc)
                
                if is_valid:
                    status_message = "Ready to capture"
                    status_color = (0, 255, 0)
                    
                    # Timed Capture
                    current_time = time.time()
                    if current_time - last_capture_time >= CAPTURE_INTERVAL:
                        samples_captured += 1
                        last_capture_time = current_time
                        
                        # Save Image
                        img_name = f"sample_{samples_captured:02d}.jpg"
                        img_path = student_folder / img_name
                        cv2.imwrite(str(img_path), frame, [int(cv2.IMWRITE_JPEG_QUALITY), IMAGE_QUALITY])
                        logger.debug(f"Saved: {img_name}")
                else:
                    status_message = reason
                    status_color = (0, 255, 255) # Yellow for warning

                # Draw box on display frame
                FrameUtils.draw_face_box(display_frame, *face_loc, label=f"Capturing: {samples_captured}/{CAPTURE_SAMPLE_COUNT}")
            
            elif len(face_locations) > 1:
                status_message = "Multiple Faces Detected!"
                status_color = (0, 0, 255)

            # UI Overlays
            FrameUtils.add_text_overlay(display_frame, f"Progress: {samples_captured}/{CAPTURE_SAMPLE_COUNT}", position=(10, 30))
            FrameUtils.add_text_overlay(display_frame, f"Status: {status_message}", position=(10, 60), color=status_color)
            FrameUtils.add_text_overlay(display_frame, "Press ESC to Cancel", position=(10, 450), color=(255, 255, 255))

            cam.show_frame("Student Registration", display_frame)

            if cv2.waitKey(1) & 0xFF == 27:
                logger.info("Registration cancelled by user.")
                break

        if samples_captured == CAPTURE_SAMPLE_COUNT:
            logger.info(f"Successfully registered {student_name} ({student_id})")
            print(f"\n✅ SUCCESS: {samples_captured} samples saved in {student_folder}")

    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
    
    finally:
        if 'cam' in locals():
            cam.cleanup()

if __name__ == "__main__":
    register_student()
