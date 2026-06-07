import os
import sys
import time
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

# Path setup for imports
ai_module_path = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
if str(ai_module_path) not in sys.path:
    sys.path.insert(0, str(ai_module_path))

from error_handler import ErrorCategory, SystemError, ErrorTracker, FrameQualityGate, RecoveryManager

@pytest.fixture
def error_tracker():
    tracker = ErrorTracker()
    tracker.clear()
    return tracker

# ==============================================================================
# Part A: ErrorTracker Tests
# ==============================================================================

def test_record_error_increments_count(error_tracker):
    """Record 3 errors, verify count is 3"""
    for i in range(3):
        err = SystemError(
            category=ErrorCategory.TRANSIENT,
            source="TestComponent",
            message=f"Transient error {i}"
        )
        error_tracker.record_error(err)
    
    summary = error_tracker.get_health_summary()
    assert summary["total_errors"] == 3


def test_error_rate_within_window(error_tracker):
    """Record errors within the time window, verify rate is calculated correctly"""
    # 5 errors in the current window should yield a rate of 5.0 errors per minute
    # (given ERROR_RATE_WINDOW_SECONDS = 60)
    for i in range(5):
        err = SystemError(
            category=ErrorCategory.TRANSIENT,
            source="TestComponent",
            message=f"Error {i}"
        )
        error_tracker.record_error(err)
        
    rate = error_tracker.get_total_error_rate()
    assert rate == pytest.approx(5.0)


def test_error_rate_expires_old_errors(error_tracker):
    """Record errors, advance time past window, verify expired errors are excluded from rate"""
    current_time = time.time()
    
    # Record error in current simulated time
    with patch("time.time", return_value=current_time):
        err = SystemError(
            category=ErrorCategory.TRANSIENT,
            source="TestComponent",
            message="Transient error"
        )
        error_tracker.record_error(err)
        assert error_tracker.get_total_error_rate() > 0
        
    # Advance time past window (60s)
    future_time = current_time + 75
    with patch("time.time", return_value=future_time):
        assert error_tracker.get_total_error_rate() == 0.0


def test_is_healthy_below_threshold(error_tracker):
    """Record few errors, verify is_healthy() returns True"""
    # Threshold is 10. Record 3 errors.
    for i in range(3):
        err = SystemError(
            category=ErrorCategory.TRANSIENT,
            source="TestComponent",
            message=f"Transient error {i}"
        )
        error_tracker.record_error(err)
        
    assert error_tracker.is_healthy() is True


def test_is_healthy_above_threshold(error_tracker):
    """Record many errors, verify is_healthy() returns False"""
    # Threshold is 10. Record 12 errors.
    for i in range(12):
        err = SystemError(
            category=ErrorCategory.TRANSIENT,
            source="TestComponent",
            message=f"Transient error {i}"
        )
        error_tracker.record_error(err)
        
    assert error_tracker.is_healthy() is False


def test_error_rate_per_source(error_tracker):
    """Record errors from different sources, verify per-source rates are correct"""
    # Source A: 3 errors
    # Source B: 2 errors
    for i in range(3):
        error_tracker.record_error(SystemError(
            category=ErrorCategory.TRANSIENT,
            source="SourceA",
            message=f"Error {i}"
        ))
    for i in range(2):
        error_tracker.record_error(SystemError(
            category=ErrorCategory.TRANSIENT,
            source="SourceB",
            message=f"Error {i}"
        ))
        
    assert error_tracker.get_error_rate("SourceA") == pytest.approx(3.0)
    assert error_tracker.get_error_rate("SourceB") == pytest.approx(2.0)
    assert error_tracker.get_error_rate("NonExistent") == 0.0


def test_health_summary_structure(error_tracker):
    """Verify get_health_summary() returns expected keys"""
    error_tracker.record_error(SystemError(
        category=ErrorCategory.TRANSIENT,
        source="TestComponent",
        message="Test message"
    ))
    
    summary = error_tracker.get_health_summary()
    assert "healthy" in summary
    assert "total_errors" in summary
    assert "total_error_rate" in summary
    assert "errors_by_source" in summary
    
    assert summary["healthy"] is True
    assert summary["total_errors"] == 1
    assert "TestComponent" in summary["errors_by_source"]
    assert summary["errors_by_source"]["TestComponent"] == 1


def test_clear_resets_all(error_tracker):
    """Record errors, call clear(), verify all counters are zero"""
    error_tracker.record_error(SystemError(
        category=ErrorCategory.TRANSIENT,
        source="TestComponent",
        message="Test message"
    ))
    
    assert error_tracker.get_total_error_rate() > 0
    error_tracker.clear()
    assert error_tracker.get_total_error_rate() == 0.0
    
    summary = error_tracker.get_health_summary()
    assert summary["total_errors"] == 0
    assert len(summary["errors_by_source"]) == 0


# ==============================================================================
# Part B: RecoveryManager Tests
# ==============================================================================

def test_webcam_reconnect_success_first_attempt():
    manager = RecoveryManager()
    mock_cam = MagicMock()
    mock_cam.reconnect.return_value = True
    
    with patch("time.sleep"):
        success = manager.attempt_webcam_reconnect(mock_cam)
        assert success is True
        assert mock_cam.reconnect.call_count == 1

def test_webcam_reconnect_success_after_retries():
    manager = RecoveryManager()
    mock_cam = MagicMock()
    mock_cam.reconnect.side_effect = [False, False, True]
    
    with patch("time.sleep"):
        success = manager.attempt_webcam_reconnect(mock_cam)
        assert success is True
        assert mock_cam.reconnect.call_count == 3

def test_webcam_reconnect_all_attempts_fail():
    manager = RecoveryManager()
    mock_cam = MagicMock()
    mock_cam.reconnect.return_value = False
    
    with patch("time.sleep"):
        success = manager.attempt_webcam_reconnect(mock_cam)
        assert success is False
        assert mock_cam.reconnect.call_count == 5

def test_encoding_reload_success():
    manager = RecoveryManager()
    mock_cache = MagicMock()
    mock_cache.is_loaded.return_value = True
    
    with patch("pathlib.Path.exists", return_value=True):
        success = manager.attempt_encoding_reload(mock_cache, "dummy_encodings.pickle")
        assert success is True
        mock_cache.load.assert_called_once_with("dummy_encodings.pickle")

def test_encoding_reload_missing_file():
    manager = RecoveryManager()
    mock_cache = MagicMock()
    
    with patch("pathlib.Path.exists", return_value=False):
        success = manager.attempt_encoding_reload(mock_cache, "non_existent.pickle")
        assert success is False
        mock_cache.load.assert_not_called()

def test_recovery_stats_tracking():
    manager = RecoveryManager()
    mock_cam = MagicMock()
    mock_cam.reconnect.return_value = True
    
    with patch("time.sleep"):
        manager.attempt_webcam_reconnect(mock_cam)
        
    mock_cache = MagicMock()
    mock_cache.is_loaded.return_value = True
    with patch("pathlib.Path.exists", return_value=True):
        manager.attempt_encoding_reload(mock_cache, "dummy.pickle")
        
    stats = manager.get_recovery_stats()
    assert stats["webcam_recovery_attempts"] == 1
    assert stats["webcam_recovery_successes"] == 1
    assert stats["encoding_reload_attempts"] == 1
    assert stats["encoding_reload_successes"] == 1

# ==============================================================================
# Part C: FrameQualityGate Tests
# ==============================================================================

def test_normal_frame_passes():
    gate = FrameQualityGate()
    import numpy as np
    dummy_frame = np.zeros((100, 100, 3), dtype=np.uint8)
    
    with patch("cv2.Laplacian") as mock_laplacian, patch("numpy.mean") as mock_mean:
        mock_var = MagicMock()
        mock_var.var.return_value = 80.0
        mock_laplacian.return_value = mock_var
        mock_mean.return_value = 120.0
        
        ok, reason = gate.check_frame(dummy_frame)
        assert ok is True

def test_dark_frame_rejected():
    gate = FrameQualityGate()
    import numpy as np
    dummy_frame = np.zeros((100, 100, 3), dtype=np.uint8)
    
    with patch("cv2.Laplacian") as mock_laplacian, patch("numpy.mean") as mock_mean:
        mock_var = MagicMock()
        mock_var.var.return_value = 100.0
        mock_laplacian.return_value = mock_var
        mock_mean.return_value = 15.0
        
        ok, reason = gate.check_frame(dummy_frame)
        assert ok is False
        assert "low lighting" in reason.lower()

def test_bright_frame_rejected():
    gate = FrameQualityGate()
    import numpy as np
    dummy_frame = np.zeros((100, 100, 3), dtype=np.uint8)
    
    with patch("cv2.Laplacian") as mock_laplacian, patch("numpy.mean") as mock_mean:
        mock_var = MagicMock()
        mock_var.var.return_value = 100.0
        mock_laplacian.return_value = mock_var
        mock_mean.return_value = 248.0
        
        ok, reason = gate.check_frame(dummy_frame)
        assert ok is False
        assert "overexposed" in reason.lower()

def test_blurry_frame_rejected():
    gate = FrameQualityGate()
    import numpy as np
    dummy_frame = np.zeros((100, 100, 3), dtype=np.uint8)
    
    with patch("cv2.Laplacian") as mock_laplacian, patch("numpy.mean") as mock_mean:
        mock_var = MagicMock()
        mock_var.var.return_value = 10.0
        mock_laplacian.return_value = mock_var
        mock_mean.return_value = 120.0
        
        ok, reason = gate.check_frame(dummy_frame)
        assert ok is False
        assert "blurry" in reason.lower()

def test_none_frame_rejected():
    gate = FrameQualityGate()
    ok, reason = gate.check_frame(None)
    assert ok is False
    assert "invalid frame" in reason.lower()

def test_empty_frame_rejected():
    gate = FrameQualityGate()
    import numpy as np
    empty_frame = np.empty((0, 0, 3), dtype=np.uint8)
    ok, reason = gate.check_frame(empty_frame)
    assert ok is False
    assert "invalid frame" in reason.lower()

def test_quality_stats_tracking():
    gate = FrameQualityGate()
    import numpy as np
    dummy_frame = np.zeros((100, 100, 3), dtype=np.uint8)
    
    with patch("cv2.Laplacian") as mock_laplacian, patch("numpy.mean") as mock_mean:
        mock_var = MagicMock()
        mock_var.var.return_value = 80.0
        mock_laplacian.return_value = mock_var
        mock_mean.return_value = 120.0
        
        gate.check_frame(dummy_frame)
        gate.check_frame(dummy_frame)
        
        mock_mean.return_value = 15.0 # dark
        gate.check_frame(dummy_frame)
        
    stats = gate.get_stats()
    assert stats["total_checked"] == 3
    assert stats["total_passed"] == 2
    assert stats["dark_rejections"] == 1
