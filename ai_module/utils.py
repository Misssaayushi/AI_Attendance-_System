import cv2
import face_recognition
from pathlib import Path
import numpy as np
import logging
import sys
import base64
import pickle
from datetime import datetime
try:
    from ai_module.config import LOG_FILE, DEBUG_MODE, RECOGNITION_TOLERANCE, UNKNOWN_LABEL
except ImportError:
    from config import LOG_FILE, DEBUG_MODE, RECOGNITION_TOLERANCE, UNKNOWN_LABEL

def get_logger(name="AI_System"):
    """
    Configures and returns a logger that writes to both console and file.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG if DEBUG_MODE else logging.INFO)

    # Prevent duplicate handlers if logger is called multiple times
    if not logger.handlers:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # File Handler
        file_handler = logging.FileHandler(LOG_FILE)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger

class FrameUtils:
    """
    Collection of utilities for frame manipulation.
    """
    @staticmethod
    def resize_frame(frame, scale=0.25):
        """
        Resizes frame for faster AI processing.
        Default is 1/4 size (faster detection).
        """
        return cv2.resize(frame, (0, 0), fx=scale, fy=scale)

    @staticmethod
    def add_text_overlay(frame, text, position=(10, 30), color=(0, 255, 0)):
        """
        Adds a text overlay to the frame.
        """
        cv2.putText(frame, text, position, cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    @staticmethod
    def draw_face_box(frame, top, right, bottom, left, label="Face"):
        """
        Draws a professional-looking bounding box around the detected face.
        """
        # Draw the main rectangle
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

        # Draw a solid background for the label
        cv2.rectangle(frame, (left, top - 30), (right, top), (0, 255, 0), cv2.FILLED)
        
        # Add the label text
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, label, (left + 6, top - 6), font, 0.6, (255, 255, 255), 1)

class FaceDetector:
    """
    Handles face detection logic using optimized frame processing.
    """
    def __init__(self, model="hog", scale=0.25):
        self.model = model
        self.scale = scale
        self.logger = get_logger("FaceDetector")

    def detect_faces(self, frame):
        """
        Detects faces in a frame after resizing and RGB conversion.
        Returns: face_locations (list of tuples)
        """
        if frame is None or frame.size == 0:
            self.logger.warning("Empty frame passed to detect_faces.")
            return []

        # 1. Resize for speed
        small_frame = cv2.resize(frame, (0, 0), fx=self.scale, fy=self.scale)

        # 2. Convert BGR to RGB (OpenCV to face_recognition format)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # 3. Detect faces
        face_locations = face_recognition.face_locations(rgb_small_frame, model=self.model)

        # 4. Scale coordinates back up
        scaled_locations = []
        for (top, right, bottom, left) in face_locations:
            # Multiply by inverse of scale (e.g., 1/0.25 = 4)
            inv_scale = int(1 / self.scale)
            scaled_locations.append((
                top * inv_scale,
                right * inv_scale,
                bottom * inv_scale,
                left * inv_scale
            ))
        
        return scaled_locations

class FaceValidator:
    """
    Validates face image quality before registration.
    """
    def __init__(self, blur_threshold=100, brightness_min=40, brightness_max=250, min_face_size=100):
        self.blur_threshold = blur_threshold
        self.brightness_min = brightness_min
        self.brightness_max = brightness_max
        self.min_face_size = min_face_size
        self.logger = get_logger("FaceValidator")

    def is_blurry(self, frame):
        """Returns True if the frame is blurry."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        score = cv2.Laplacian(gray, cv2.CV_64F).var()
        return score < self.blur_threshold

    def get_brightness(self, frame):
        """Returns the average brightness of the frame."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return np.mean(gray)

    def validate(self, frame, face_location):
        """
        Runs all quality checks.
        Returns: (bool, str) - (Success, Reason/Message)
        """
        top, right, bottom, left = face_location
        width = right - left
        height = bottom - top

        # 1. Check Face Size
        if width < self.min_face_size or height < self.min_face_size:
            return False, "Too far from camera"

        # 2. Check Brightness
        brightness = self.get_brightness(frame)
        if brightness < self.brightness_min:
            return False, "Too dark"
        if brightness > self.brightness_max:
            return False, "Too much light"

        # 3. Check Blur
        if self.is_blurry(frame):
            return False, "Keep steady (Blurry)"

        return True, "Ready"

class EncodingManager:
    """
    Handles loading and managing face encodings from disk to memory.
    """
    def __init__(self, encoding_file):
        self.encoding_file = Path(encoding_file)
        self.known_encodings = []
        self.known_names = []
        self.logger = get_logger("EncodingManager")
        self.load_known_faces()

    def load_known_faces(self):
        """
        Loads the consolidated encoding file into memory.
        """
        if not self.encoding_file.exists():
            self.logger.warning(f"Encoding file {self.encoding_file} not found. Recognition will not work.")
            return

        try:
            with open(self.encoding_file, "rb") as f:
                data = pickle.load(f)
            
            self.known_encodings = data.get("encodings", [])
            self.known_names = data.get("names", [])
            self.logger.info(f"Loaded {len(self.known_names)} face encodings into memory.")
        except Exception as e:
            self.logger.error(f"Failed to load encodings: {str(e)}")

class FaceRecognizer:
    """
    Core recognition engine that compares live faces with the encoding database.
    """
    def __init__(self, encoding_manager, tolerance=RECOGNITION_TOLERANCE):
        self.manager = encoding_manager
        self.tolerance = tolerance
        self.logger = get_logger("FaceRecognizer")

    def identify(self, frame, face_location):
        """
        Generates encoding for a detected face and finds the best match.
        Returns: name (str), confidence (float)
        """
        if not self.manager.known_encodings:
            return UNKNOWN_LABEL, 0.0

        # Generate encoding for the live face
        # Note: face_recognition.face_encodings expects a list of locations
        live_encodings = face_recognition.face_encodings(frame, [face_location])
        
        if not live_encodings:
            return UNKNOWN_LABEL, 0.0
        
        live_encoding = live_encodings[0]

        # 1. Check for matches
        matches = face_recognition.compare_faces(
            self.manager.known_encodings, 
            live_encoding, 
            tolerance=self.tolerance
        )
        
        name = UNKNOWN_LABEL
        
        # 2. Use face distance to find the best match
        face_distances = face_recognition.face_distance(self.manager.known_encodings, live_encoding)
        best_match_index = np.argmin(face_distances)
        
        if matches[best_match_index]:
            name = self.manager.known_names[best_match_index]
            # Convert distance to a simple "Confidence" percentage
            # (1 - distance) * 100
            confidence = (1 - face_distances[best_match_index]) * 100
            return name, confidence

        return UNKNOWN_LABEL, 0.0

class CameraHandler:
    """
    Handles webcam initialization, frame reading, and resource cleanup.
    """
    def __init__(self, camera_id=0):
        self.camera_id = camera_id
        self.cap = cv2.VideoCapture(self.camera_id)
        self.logger = get_logger("CameraHandler")

        if not self.cap.isOpened():
            self.logger.error(f"Could not open webcam with ID: {self.camera_id}")
            raise Exception(f"Webcam ID {self.camera_id} not available.")
        
        self.logger.info(f"Webcam {self.camera_id} initialized successfully.")

    def get_frame(self):
        """
        Reads a frame from the webcam.
        Returns: ret (bool), frame (numpy.ndarray)
        """
        ret, frame = self.cap.read()
        if not ret:
            self.logger.warning("Failed to read frame from webcam.")
        return ret, frame

    def show_frame(self, window_name, frame):
        """
        Displays the frame in a window.
        """
        cv2.imshow(window_name, frame)

    def cleanup(self):
        """
        Releases the webcam and closes windows.
        """
        self.cap.release()
        cv2.destroyAllWindows()
        self.logger.info("Webcam resources released.")

class Base64Utils:
    """
    Utilities for converting between Base64 strings (Frontend) 
    and OpenCV images (AI Module).
    """
    @staticmethod
    def base64_to_cv2(b64_string):
        """
        Converts a Base64 string (from React) to an OpenCV BGR image.
        """
        try:
            if "base64," in b64_string:
                b64_string = b64_string.split("base64,")[1]
            
            img_data = base64.b64decode(b64_string)
            nparr = np.frombuffer(img_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return frame
        except Exception as e:
            get_logger("Base64Utils").error(f"Base64 conversion failed: {str(e)}")
            return None

    @staticmethod
    def cv2_to_base64(frame):
        """
        Converts an OpenCV BGR image to a Base64 string.
        """
        try:
            _, buffer = cv2.imencode('.jpg', frame)
            b64_string = base64.b64encode(buffer).decode('utf-8')
            return f"data:image/jpeg;base64,{b64_string}"
        except Exception as e:
            get_logger("Base64Utils").error(f"CV2 to Base64 conversion failed: {str(e)}")
            return None
