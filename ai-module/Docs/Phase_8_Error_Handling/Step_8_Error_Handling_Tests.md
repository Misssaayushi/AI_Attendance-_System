# Step 8: Error Handling Test Suite

## Objective
Create `tests/test_error_handling.py` with comprehensive pytest tests covering `ErrorTracker`, `RecoveryManager`, and `FrameQualityGate` from `error_handler.py`.

## Why This Step
Every error handling component must be validated to ensure it behaves correctly under failure conditions. Without tests, we can't be confident that:
- Error rates are calculated correctly
- Health thresholds trigger at the right time
- Webcam recovery follows the correct backoff pattern
- Frame quality gate rejects bad frames and passes good ones

## Tasks

### Part A: ErrorTracker Tests (~8 tests)

1. `test_record_error_increments_count` — Record 3 errors, verify count is 3
2. `test_error_rate_within_window` — Record errors within the time window, verify rate is calculated correctly
3. `test_error_rate_expires_old_errors` — Record errors, advance time past window, verify expired errors are excluded from rate
4. `test_is_healthy_below_threshold` — Record few errors, verify `is_healthy()` returns `True`
5. `test_is_healthy_above_threshold` — Record many errors, verify `is_healthy()` returns `False`
6. `test_error_rate_per_source` — Record errors from different sources, verify per-source rates are correct
7. `test_health_summary_structure` — Verify `get_health_summary()` returns expected keys
8. `test_clear_resets_all` — Record errors, call `clear()`, verify all counters are zero

### Part B: RecoveryManager Tests (~6 tests)

9. `test_webcam_reconnect_success_first_attempt` — Mock `camera_handler.reconnect()` to return `True`, verify success on first attempt
10. `test_webcam_reconnect_success_after_retries` — Mock reconnect to fail twice then succeed, verify exponential backoff delays
11. `test_webcam_reconnect_all_attempts_fail` — Mock reconnect to always fail, verify returns `False` after max attempts
12. `test_encoding_reload_success` — Provide valid encoding file, verify reload returns `True`
13. `test_encoding_reload_missing_file` — Provide non-existent path, verify returns `False` without crash
14. `test_recovery_stats_tracking` — Perform multiple recoveries, verify stats dictionary is correct

### Part C: FrameQualityGate Tests (~7 tests)

15. `test_normal_frame_passes` — Create frame with moderate brightness and no blur, verify passes
16. `test_dark_frame_rejected` — Create very dark frame (mean ~10), verify rejected with "Low lighting" message
17. `test_bright_frame_rejected` — Create very bright frame (mean ~250), verify rejected with "Overexposed" message
18. `test_blurry_frame_rejected` — Create heavily blurred frame, verify rejected with "blurry" message
19. `test_none_frame_rejected` — Pass `None`, verify rejected with "Invalid frame" message
20. `test_empty_frame_rejected` — Pass 0×0 ndarray, verify rejected gracefully
21. `test_quality_stats_tracking` — Process multiple frames, verify `get_stats()` returns correct pass/reject counts

## Test Structure

```python
import pytest
import numpy as np
import time
from unittest.mock import MagicMock, patch

# Path setup for imports
import os, sys
from pathlib import Path
ai_module_path = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
if str(ai_module_path) not in sys.path:
    sys.path.insert(0, str(ai_module_path))

from error_handler import ErrorCategory, SystemError, ErrorTracker, RecoveryManager, FrameQualityGate

@pytest.fixture
def error_tracker():
    tracker = ErrorTracker()
    tracker.clear()
    return tracker

@pytest.fixture
def recovery_manager():
    return RecoveryManager()

@pytest.fixture
def quality_gate():
    return FrameQualityGate()
```

## Dependencies
- Step 2 (ErrorTracker, ErrorCategory, SystemError)
- Step 4 (RecoveryManager)
- Step 5 (FrameQualityGate)

## Files Created
- `ai_module/tests/test_error_handling.py`

## Expected Outcome
21 passing pytest tests that validate all error handling components work correctly under normal, edge, and failure conditions. Running `pytest tests/test_error_handling.py -v` produces all green results.
