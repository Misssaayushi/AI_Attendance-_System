import time
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
import threading
from typing import Optional, Dict, Any, List
from pathlib import Path
import cv2
import numpy as np

try:
    from ai_module.config import (
        ERROR_RATE_WINDOW_SECONDS, ERROR_RATE_THRESHOLD,
        WEBCAM_RECONNECT_BASE_DELAY, WEBCAM_RECONNECT_MAX_DELAY, WEBCAM_MAX_RECONNECT_ATTEMPTS,
        ENABLE_FRAME_QUALITY_GATE, QUALITY_GATE_BLUR_THRESHOLD,
        QUALITY_GATE_BRIGHTNESS_MIN, QUALITY_GATE_BRIGHTNESS_MAX
    )
    from ai_module.utils import get_logger
except ImportError:
    from config import (
        ERROR_RATE_WINDOW_SECONDS, ERROR_RATE_THRESHOLD,
        WEBCAM_RECONNECT_BASE_DELAY, WEBCAM_RECONNECT_MAX_DELAY, WEBCAM_MAX_RECONNECT_ATTEMPTS,
        ENABLE_FRAME_QUALITY_GATE, QUALITY_GATE_BLUR_THRESHOLD,
        QUALITY_GATE_BRIGHTNESS_MIN, QUALITY_GATE_BRIGHTNESS_MAX
    )
    from utils import get_logger

class ErrorCategory(Enum):
    TRANSIENT = "TRANSIENT"      # retryable errors that resolve on their own (e.g., single frame read failure)
    RECOVERABLE = "RECOVERABLE"  # errors that need a recovery action (e.g., webcam disconnect)
    FATAL = "FATAL"              # errors where the system cannot continue (e.g., no camera device exists)

@dataclass
class SystemError:
    category: ErrorCategory
    source: str
    message: str
    timestamp: float = field(default_factory=time.time)
    exception: Optional[Exception] = None

class ErrorTracker:
    def __init__(self):
        self._errors = deque()
        self._lock = threading.Lock()
        self.logger = get_logger("ErrorTracker")

    def _prune_expired(self):
        """
        Removes errors that are older than ERROR_RATE_WINDOW_SECONDS.
        Must be called with the lock acquired or inside locked methods.
        """
        now = time.time()
        cutoff = now - ERROR_RATE_WINDOW_SECONDS
        while self._errors and self._errors[0].timestamp < cutoff:
            self._errors.popleft()

    def record_error(self, error: SystemError):
        """
        Logs the error using the appropriate level and appends it to the tracker.
        """
        # Formulate a log message
        log_msg = f"[{error.source}] {error.message}"
        if error.exception:
            log_msg += f" | Exception: {type(error.exception).__name__}: {str(error.exception)}"

        # Select appropriate logger severity
        if error.category == ErrorCategory.TRANSIENT:
            self.logger.warning(log_msg)
        elif error.category == ErrorCategory.RECOVERABLE:
            self.logger.error(log_msg)
        elif error.category == ErrorCategory.FATAL:
            self.logger.critical(log_msg)
        else:
            self.logger.error(log_msg)

        with self._lock:
            self._errors.append(error)
            self._prune_expired()

    def get_error_rate(self, source: str) -> float:
        """
        Returns errors per minute for a specific source within the configured window.
        """
        with self._lock:
            self._prune_expired()
            count = sum(1 for e in self._errors if e.source == source)
            window_minutes = max(ERROR_RATE_WINDOW_SECONDS, 1) / 60.0
            return count / window_minutes

    def get_total_error_rate(self) -> float:
        """
        Returns aggregate errors per minute across all sources.
        """
        with self._lock:
            self._prune_expired()
            count = len(self._errors)
            window_minutes = max(ERROR_RATE_WINDOW_SECONDS, 1) / 60.0
            return count / window_minutes

    def is_healthy(self) -> bool:
        """
        Returns True if total error rate is below ERROR_RATE_THRESHOLD.
        """
        return self.get_total_error_rate() < ERROR_RATE_THRESHOLD

    def get_health_summary(self) -> dict:
        """
        Returns a snapshot dict with health details.
        """
        with self._lock:
            self._prune_expired()
            total_errors = len(self._errors)
            
            # Count by source
            errors_by_source = {}
            for e in self._errors:
                errors_by_source[e.source] = errors_by_source.get(e.source, 0) + 1
                
            window_minutes = max(ERROR_RATE_WINDOW_SECONDS, 1) / 60.0
            total_error_rate = total_errors / window_minutes
            healthy = total_error_rate < ERROR_RATE_THRESHOLD
            
            return {
                "healthy": healthy,
                "total_errors": total_errors,
                "total_error_rate": total_error_rate,
                "errors_by_source": errors_by_source
            }

    def clear(self):
        """
        Resets all tracked errors (useful for testing).
        """
        with self._lock:
            self._errors.clear()

# Default global singleton instance
error_tracker = ErrorTracker()

class RecoveryManager:
    def __init__(self):
        self._webcam_attempts = 0
        self._webcam_successes = 0
        self._encoding_attempts = 0
        self._encoding_successes = 0
        self.logger = get_logger("RecoveryManager")

    def attempt_webcam_reconnect(self, camera_handler) -> bool:
        """
        Attempts to reconnect the webcam using exponential backoff.
        """
        delay = WEBCAM_RECONNECT_BASE_DELAY
        for attempt in range(1, WEBCAM_MAX_RECONNECT_ATTEMPTS + 1):
            self._webcam_attempts += 1
            self.logger.info(f"Webcam recovery attempt {attempt}/{WEBCAM_MAX_RECONNECT_ATTEMPTS}. Waiting {delay}s...")
            time.sleep(delay)
            
            if camera_handler.reconnect():
                self._webcam_successes += 1
                self.logger.info("Webcam recovered successfully.")
                return True
                
            delay = min(delay * 2.0, WEBCAM_RECONNECT_MAX_DELAY)
            
        self.logger.error("Webcam recovery failed after max attempts.")
        return False

    def attempt_encoding_reload(self, encoding_cache, path) -> bool:
        """
        Attempts to reload the encoding file safely.
        """
        self._encoding_attempts += 1
        path_obj = Path(path)
        if not path_obj.exists():
            self.logger.warning(f"Encoding file {path} not found during recovery.")
            return False
            
        try:
            encoding_cache.load(path)
            if encoding_cache.is_loaded():
                self._encoding_successes += 1
                return True
            else:
                self.logger.error(f"Encoding file {path} corrupted or invalid.")
                return False
        except Exception as e:
            self.logger.error(f"Encoding file {path} corrupted or invalid: {e}")
            return False

    def get_recovery_stats(self) -> dict:
        return {
            "webcam_recovery_attempts": self._webcam_attempts,
            "webcam_recovery_successes": self._webcam_successes,
            "encoding_reload_attempts": self._encoding_attempts,
            "encoding_reload_successes": self._encoding_successes
        }


class FrameQualityGate:
    def __init__(self):
        self._total_checked = 0
        self._total_passed = 0
        self._blur_rejections = 0
        self._dark_rejections = 0
        self._bright_rejections = 0
        self._invalid_rejections = 0
        self.logger = get_logger("FrameQualityGate")

    def check_frame(self, frame) -> tuple[bool, str]:
        """
        Validates frame quality (blurriness and brightness/lighting).
        Returns (True, "OK") if it passes all checks, or (False, reason) if it fails.
        """
        self._total_checked += 1
        
        if frame is None:
            self._invalid_rejections += 1
            return False, "Invalid frame"
            
        try:
            # Check if frame is empty
            if frame.size == 0:
                self._invalid_rejections += 1
                return False, "Invalid frame"
                
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # 1. Blur check: Laplacian variance
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            if laplacian_var < QUALITY_GATE_BLUR_THRESHOLD:
                self._blur_rejections += 1
                return False, "Frame too blurry"
                
            # 2. Brightness checks: mean intensity
            mean_brightness = np.mean(gray)
            if mean_brightness < QUALITY_GATE_BRIGHTNESS_MIN:
                self._dark_rejections += 1
                return False, "Low lighting detected"
            elif mean_brightness > QUALITY_GATE_BRIGHTNESS_MAX:
                self._bright_rejections += 1
                return False, "Overexposed frame"
                
            self._total_passed += 1
            return True, "OK"
        except Exception as e:
            self._invalid_rejections += 1
            self.logger.error(f"Error checking frame quality: {e}")
            return False, f"Quality check error: {str(e)}"

    def get_stats(self) -> dict:
        """
        Returns stats about frame checks and rejections.
        """
        rejections = self._total_checked - self._total_passed
        pass_rate = (self._total_passed / self._total_checked * 100.0) if self._total_checked > 0 else 100.0
        return {
            "total_checked": self._total_checked,
            "total_passed": self._total_passed,
            "total_rejected": rejections,
            "blur_rejections": self._blur_rejections,
            "dark_rejections": self._dark_rejections,
            "bright_rejections": self._bright_rejections,
            "invalid_rejections": self._invalid_rejections,
            "pass_rate": pass_rate
        }


# Default global singleton instance
frame_quality_gate = FrameQualityGate()
