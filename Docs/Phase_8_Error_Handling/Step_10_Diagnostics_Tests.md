# Step 10: Diagnostics Test Suite

## Objective
Create `tests/test_diagnostics.py` with pytest tests covering `FrameSimulator`, `RecognitionStabilityTester`, `PerformanceValidator`, and `SystemHealthChecker` from `diagnostics.py`.

## Why This Step
The diagnostics module provides testing utilities — but those utilities themselves need to be tested to ensure they produce correct results. A `FrameSimulator` that generates frames with wrong brightness values would invalidate all downstream testing.

## Tasks

### Part A: FrameSimulator Tests (~5 tests)

1. `test_normal_frame_dimensions` — Verify `create_normal_frame(640, 480)` returns shape `(480, 640, 3)` with dtype `uint8`
2. `test_dark_frame_brightness` — Verify `create_dark_frame()` has mean pixel intensity < `QUALITY_GATE_BRIGHTNESS_MIN` (30)
3. `test_bright_frame_brightness` — Verify `create_bright_frame()` has mean pixel intensity > `QUALITY_GATE_BRIGHTNESS_MAX` (245)
4. `test_blurry_frame_variance` — Verify `create_blurry_frame()` has Laplacian variance < `QUALITY_GATE_BLUR_THRESHOLD` (50)
5. `test_add_noise_preserves_shape` — Verify `add_noise(frame, 0.1)` returns same shape and dtype as input

### Part B: RecognitionStabilityTester Tests (~4 tests)

6. `test_consistency_with_identical_encodings` — Mock recognizer to always return same name:
   - Feed same encoding 50 times
   - Verify `consistency_pct` is 100.0%
   - Verify `mismatches` is 0

7. `test_consistency_with_flaky_recognizer` — Mock recognizer to return different names 20% of the time:
   - Verify `consistency_pct` is approximately 80%
   - Verify `mismatches` is approximately 10 (out of 50)

8. `test_confidence_stability_within_bounds` — Mock recognizer with small confidence variation:
   - Verify `confidence_std` < 5.0
   - Verify `stable` is `True`

9. `test_multi_face_no_crash` — Pass 5 mock encodings:
   - Verify all 5 are processed
   - Verify `failures` is 0
   - Verify `avg_time_ms` is a positive float

### Part C: PerformanceValidator Tests (~3 tests)

10. `test_fps_stability_under_normal_conditions` — Create `PerformanceTracker` with consistent tick intervals:
    - Run `validate_fps_stability()` with 100 ticks
    - Verify `fps_std` is within 20% of mean
    - Verify `stable` is `True`

11. `test_memory_stability_no_growth` — Run `validate_memory_stability()` with 100 iterations:
    - Verify `growth_per_iteration` < 1000 bytes (allow for Python overhead)
    - Verify `stable` is `True`

12. `test_diagnostics_report_generation` — Run `generate_diagnostics_report()` to temp directory:
    - Verify file is created
    - Verify file contains expected sections (system info, performance, memory)
    - Clean up temp file

### Part D: SystemHealthChecker Tests (~3 tests)

13. `test_check_dependencies_passes` — Verify `check_dependencies()` returns `(True, ...)` since cv2/numpy/face_recognition are installed
14. `test_check_encodings_missing_file` — Verify `check_encodings("nonexistent.pkl")` returns `(False, ...)`
15. `test_run_all_checks_structure` — Verify `run_all_checks()` returns dict with all expected keys: `camera`, `encodings`, `dependencies`, `disk_space`, `overall_healthy`

## Test Structure

```python
import pytest
import numpy as np
import time
import os, sys, tempfile
from pathlib import Path
from unittest.mock import MagicMock

ai_module_path = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
if str(ai_module_path) not in sys.path:
    sys.path.insert(0, str(ai_module_path))

from diagnostics import (
    FrameSimulator, RecognitionStabilityTester,
    PerformanceValidator, SystemHealthChecker
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
```

## Dependencies
- Step 7 (diagnostics.py module)
- Step 1 (config values for thresholds)

## Files Created
- `ai_module/tests/test_diagnostics.py`

## Expected Outcome
15 passing pytest tests that validate all diagnostic utilities produce correct outputs. Running `pytest tests/test_diagnostics.py -v` produces all green results.
