import cv2
import logging
import sys
from datetime import datetime
from ai_module.config import LOG_FILE, DEBUG_MODE

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
