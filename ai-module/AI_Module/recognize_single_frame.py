import sys
import json
import warnings
import os
import cv2

# Suppress warnings that might corrupt JSON stdout
warnings.filterwarnings("ignore")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

try:
    import face_recognition
    from ai_module.utils import FaceDetector, EncodingManager, FaceRecognizer
    from ai_module.config import ENCODING_FILE, FACE_DETECTION_MODEL, FRAME_RESIZE_SCALE, RECOGNITION_TOLERANCE
except ImportError:
    # Fallback if run directly in the folder
    from utils import FaceDetector, EncodingManager, FaceRecognizer
    from config import ENCODING_FILE, FACE_DETECTION_MODEL, FRAME_RESIZE_SCALE, RECOGNITION_TOLERANCE

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"status": "error", "message": "No image path provided"}))
        sys.exit(1)

    image_path = sys.argv[1]

    if not os.path.exists(image_path):
        print(json.dumps({"status": "error", "message": "Image file not found"}))
        sys.exit(1)

    try:
        # Load image via cv2 (better compatibility with existing FaceDetector)
        frame = cv2.imread(image_path)
        if frame is None:
            print(json.dumps({"status": "error", "message": "Failed to load image"}))
            sys.exit(1)

        # Detect faces
        detector = FaceDetector(model=FACE_DETECTION_MODEL, scale=FRAME_RESIZE_SCALE)
        face_locations = detector.detect_faces(frame)

        if not face_locations:
            print(json.dumps({"status": "no_face_found"}))
            sys.exit(0)

        # We take the largest face or the first one. For simplicity, the first one.
        # But wait, FaceDetector returns a list of locations.
        # Convert BGR to RGB for face_recognition encoding generation inside identify
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Load encodings
        manager = EncodingManager(encoding_file=ENCODING_FILE)
        recognizer = FaceRecognizer(encoding_manager=manager, tolerance=RECOGNITION_TOLERANCE)

        best_name = "Unknown"
        best_confidence = 0.0
        best_box = None

        for face_loc in face_locations:
            name, confidence = recognizer.identify(rgb_frame, face_loc)
            if name != "Unknown" and confidence > best_confidence:
                best_name = name
                best_confidence = confidence
                best_box = face_loc

        if best_name == "Unknown":
            print(json.dumps({"status": "unrecognized", "confidence": 0.0}))
        else:
            print(json.dumps({
                "status": "success",
                "student_id": best_name.split('_')[0] if '_' in best_name else best_name,
                "name": best_name,
                "confidence": best_confidence,
                "box": best_box
            }))

    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    main()
