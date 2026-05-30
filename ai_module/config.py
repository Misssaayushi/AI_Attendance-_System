import os
from pathlib import Path

# Base directory for the AI module
BASE_DIR = Path(__file__).resolve().parent

# Directory Paths
DATASET_DIR = BASE_DIR / "dataset"
ENCODINGS_DIR = BASE_DIR / "encodings"
LOGS_DIR = BASE_DIR / "logs"
BENCHMARK_REPORT_DIR = BASE_DIR / "reports"

# Ensure directories exist
for folder in [DATASET_DIR, ENCODINGS_DIR, LOGS_DIR, BENCHMARK_REPORT_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

# Webcam Settings
CAMERA_ID = 0  # Default webcam
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# Recognition Settings
# Lower tolerance = stricter matching, Higher tolerance = more loose
RECOGNITION_TOLERANCE = 0.6  
ENCODING_FILE = ENCODINGS_DIR / "encodings.pickle"
RECOGNITION_PROCESS_INTERVAL = 10  # Process every 10th frame (Smoother video)
UNKNOWN_LABEL = "Unknown Person"

# Attendance Verification Settings
ATTENDANCE_COOLDOWN_MINUTES = 30  # Wait time before re-marking a student
MIN_CONFIDENCE_THRESHOLD = 80     # Minimum % confidence to verify
STABILITY_FRAMES = 3              # Consecutive frames needed to confirm

# Face Detection Settings
# Model: "hog" (CPU friendly) or "cnn" (GPU required)
FACE_DETECTION_MODEL = "hog"
FRAME_RESIZE_SCALE = 0.25  # Increased slightly for better small-face detection

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

# API Integration Settings (Phase 6)
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
ATTENDANCE_VERIFY_ENDPOINT = os.getenv("ATTENDANCE_VERIFY_ENDPOINT", "/api/v1/attendance/verify")
ATTENDANCE_VERIFY_URL = f"{API_BASE_URL.rstrip('/')}{ATTENDANCE_VERIFY_ENDPOINT}"

# API Reliability Settings
API_TIMEOUT_SECONDS = float(os.getenv("API_TIMEOUT_SECONDS", "2.0"))
API_RETRY_COUNT = int(os.getenv("API_RETRY_COUNT", "1"))
API_RETRY_DELAY_SECONDS = float(os.getenv("API_RETRY_DELAY_SECONDS", "0.25"))

# API Mock Settings
API_MOCK_MODE = os.getenv("API_MOCK_MODE", "false").lower() == "true"
API_MOCK_FORCE_FAILURE = os.getenv("API_MOCK_FORCE_FAILURE", "false").lower() == "true"
API_MOCK_RESPONSE_DELAY_SECONDS = float(os.getenv("API_MOCK_RESPONSE_DELAY_SECONDS", "0.10"))

# API Feedback Overlay Settings
API_FEEDBACK_DISPLAY_SECONDS = float(os.getenv("API_FEEDBACK_DISPLAY_SECONDS", "3.0"))
API_SUCCESS_MESSAGE = os.getenv("API_SUCCESS_MESSAGE", "Attendance Logged")
API_ERROR_MESSAGE = os.getenv("API_ERROR_MESSAGE", "Server Error")

# Phase 7: Recognition Optimization Settings
TARGET_FPS = 20                       # Target frames per second for adaptive tuning
MIN_PROCESS_INTERVAL = 3              # Minimum frames between processing
MAX_PROCESS_INTERVAL = 15             # Maximum frames between processing
ENABLE_ADAPTIVE_INTERVAL = True       # Toggle adaptive vs. fixed interval
FACE_CROP_PADDING = 30                # Pixels of context around face for crop-then-encode
ENCODING_RELOAD_CHECK_SECONDS = 30     # How often to check for file changes
ENCODING_CACHE_ENABLED = True         # Toggle singleton cache
API_DISPATCH_ASYNC = True             # Toggle non-blocking API calls
ENABLE_FPS_OVERLAY = True             # Show FPS on video feed in debug mode
PERF_TRACKER_WINDOW = 30              # Rolling average window (frames)
API_FEEDBACK_CLEANUP_INTERVAL = 100   # Frames between memory cleanup
