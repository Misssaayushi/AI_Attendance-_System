import os
from pathlib import Path

# Base directory for the AI module
BASE_DIR = Path(__file__).resolve().parent

# Directory Paths
DATASET_DIR = BASE_DIR / "dataset"
ENCODINGS_DIR = BASE_DIR / "encodings"
LOGS_DIR = BASE_DIR / "logs"

# Ensure directories exist
for folder in [DATASET_DIR, ENCODINGS_DIR, LOGS_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

# Webcam Settings
CAMERA_ID = 0  # Default webcam
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# Recognition Settings
# Lower tolerance = stricter matching, Higher tolerance = more loose
RECOGNITION_TOLERANCE = 0.6  
ENCODING_FILE = ENCODINGS_DIR / "encodings.pickle"

# Face Detection Settings
# Model: "hog" (CPU friendly) or "cnn" (GPU required)
FACE_DETECTION_MODEL = "hog"
FRAME_RESIZE_SCALE = 0.25  # Process at 1/4 size for speed

# Registration Settings
CAPTURE_SAMPLE_COUNT = 20    # Number of images per student
CAPTURE_INTERVAL = 0.5       # Seconds between captures
CAPTURE_TIMEOUT = 60         # Max time in seconds
MIN_FACE_SIZE = 100          # Min pixels for face box
BLUR_THRESHOLD = 100         # Higher = stricter (less blur allowed)
BRIGHTNESS_MIN = 40          # Min average pixel intensity
BRIGHTNESS_MAX = 250         # Max average pixel intensity
IMAGE_QUALITY = 90           # JPEG quality (0-100)

# Logging Settings
LOG_FILE = LOGS_DIR / "ai_system.log"
DEBUG_MODE = True
