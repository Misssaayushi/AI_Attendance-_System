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

# Logging Settings
LOG_FILE = LOGS_DIR / "ai_system.log"
DEBUG_MODE = True
