import os
import sys
import tempfile
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import cv2
import numpy as np
import pytest

# Path setup for imports
ai_module_path = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
if str(ai_module_path) not in sys.path:
    sys.path.insert(0, str(ai_module_path))

from diagnostics import (
    FrameSimulator,
    PerformanceValidator,
    RecognitionStabilityTester,
    SystemHealthChecker,
)
from optimization import PerformanceTracker


@pytest.fixture
def simulator():
    return FrameSimulator()


@pytest.fixture
def stability_tester():
    return RecognitionStabilityTester()


@pytest.fixture
def perf_validator():
    return PerformanceValidator()


@pytest.fixture
def health_checker():
    return SystemHealthChecker()


# ==============================================================================
# Part A: FrameSimulator Tests
# ==============================================================================

def test_normal_frame_dimensions(simulator):
    frame = simulator.create_normal_frame(640, 480)
    assert frame.shape == (480, 640, 3)
    assert frame.dtype == np.uint8


def test_dark_frame_brightness(simulator):
    frame = simulator.create_dark_frame()
    mean_intensity = np.mean(frame)
    assert mean_intensity < 30


def test_bright_frame_brightness(simulator):
    frame = simulator.create_bright_frame()
    mean_intensity = np.mean(frame)
    assert mean_intensity > 245


def test_blurry_frame_variance(simulator):
    frame = simulator.create_blurry_frame()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    variance = cv2.Laplacian(gray, cv2.CV_64F).var()
    assert variance < 50


def test_add_noise_preserves_shape(simulator):
    frame = simulator.create_normal_frame(640, 480)
    noisy_frame = simulator.add_noise(frame, 0.1)
    assert noisy_frame.shape == (480, 640, 3)
    assert noisy_frame.dtype == np.uint8


# ==============================================================================
# Part B: RecognitionStabilityTester Tests
# ==============================================================================

def test_consistency_with_identical_encodings(stability_tester):
    mock_recognizer = MagicMock()
    mock_recognizer.identify_optimized.return_value = ("Student_A", 0.95)
    encoding = np.zeros(128)

    results = stability_tester.test_consistency(mock_recognizer, encoding, iterations=50)
    assert results["consistency_pct"] == 100.0
    assert results["mismatches"] == 0
    assert results["confidence_mean"] == pytest.approx(0.95)


def test_consistency_with_flaky_recognizer(stability_tester):
    mock_recognizer = MagicMock()
    # Return incorrect name 20% of the time (1 out of 5)
    mock_recognizer.identify_optimized.side_effect = [
        ("Student_A", 0.95), ("Student_A", 0.95), ("Student_A", 0.95), ("Student_A", 0.95), ("Unknown", 0.0)
    ] * 10
    encoding = np.zeros(128)

    results = stability_tester.test_consistency(mock_recognizer, encoding, iterations=50)
    assert results["consistency_pct"] == 80.0
    assert results["mismatches"] == 10


def test_confidence_stability_within_bounds(stability_tester):
    mock_recognizer = MagicMock()
    # Simulate slightly varying confidence
    def mock_identify(enc):
        # returns confidence between 0.90 and 0.94
        return ("Student_A", 0.92 + np.random.uniform(-0.02, 0.02))
    
    mock_recognizer.identify_optimized.side_effect = mock_identify
    encoding = np.zeros(128)

    results = stability_tester.test_confidence_stability(mock_recognizer, encoding, iterations=50)
    assert results["confidence_std"] < 0.05
    assert results["stable"] is True


def test_multi_face_no_crash(stability_tester):
    mock_recognizer = MagicMock()
    mock_recognizer.identify_optimized.return_value = ("Student_A", 0.95)
    encodings = [np.zeros(128) for _ in range(5)]

    results = stability_tester.test_multi_face_handling(mock_recognizer, encodings, iterations=10)
    assert results["total_faces"] == 50
    assert results["failures"] == 0
    assert results["avg_time_ms"] > 0.0


# ==============================================================================
# Part C: PerformanceValidator Tests
# ==============================================================================

def test_fps_stability_under_normal_conditions(perf_validator):
    tracker = MagicMock()
    tracker.get_fps.side_effect = [30.0 + np.random.uniform(-1, 1) for _ in range(100)]
    
    results = perf_validator.validate_fps_stability(tracker, duration_ticks=100)
    assert results["stable"] is True


def test_memory_stability_no_growth(perf_validator):
    results = perf_validator.validate_memory_stability(iterations=100)
    # Expected growth < 2048 bytes per iteration
    assert results["growth_per_iteration"] < 2048
    assert results["stable"] is True


def test_diagnostics_report_generation(perf_validator):
    with tempfile.TemporaryDirectory() as temp_dir:
        report_path = perf_validator.generate_diagnostics_report(output_dir=temp_dir)
        
        assert os.path.exists(report_path)
        with open(report_path, "r") as f:
            content = f.read()
            assert "AI System Diagnostics Report" in content
            assert "Status: GENERATED" in content


# ==============================================================================
# Part D: SystemHealthChecker Tests
# ==============================================================================

def test_check_dependencies_passes(health_checker):
    # This should pass assuming cv2, numpy, and face_recognition are installed
    ok, msg = health_checker.check_dependencies()
    assert ok is True
    assert "critical dependencies installed" in msg


def test_check_encodings_missing_file(health_checker):
    ok, msg = health_checker.check_encodings("nonexistent.pkl")
    assert ok is False
    assert "not found" in msg


def test_run_all_checks_structure(health_checker):
    with patch.object(SystemHealthChecker, "check_camera", return_value=(True, "OK")), \
         patch.object(SystemHealthChecker, "check_encodings", return_value=(True, "OK")), \
         patch.object(SystemHealthChecker, "check_dependencies", return_value=(True, "OK")), \
         patch.object(SystemHealthChecker, "check_disk_space", return_value=(True, "OK")):
         
        results = health_checker.run_all_checks()
        
    assert "camera" in results
    assert "encodings" in results
    assert "dependencies" in results
    assert "disk_space" in results
    assert "overall_healthy" in results
    assert results["overall_healthy"] is True
