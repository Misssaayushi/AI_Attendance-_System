# Step 9: Edge Case Test Suite

## Objective
Create `tests/test_edge_cases.py` with pytest tests that exercise the system under extreme and unusual conditions — validating that the AI pipeline never crashes regardless of input quality.

## Why This Step
Real-world attendance scenarios produce many edge cases that are hard to test manually:
- A student walks in with the encoding file deleted
- The camera produces a corrupted frame
- 10 students crowd in front of the camera simultaneously
- An unknown person stands in front of the camera for 5 minutes straight

Each of these must produce graceful behavior, not crashes.

## Tasks

### Part A: Encoding Edge Cases (~5 tests)

1. `test_empty_encoding_file` — Create a pickle file with `{"encodings": [], "names": []}`:
   - Load into `EncodingCache`
   - Verify `is_loaded()` returns `True` (file is valid, just empty)
   - Verify `get_encodings()` returns shape `(0, 128)` and empty names
   - Verify `FaceRecognizer.identify_optimized()` returns `(UNKNOWN_LABEL, 0.0)`

2. `test_mismatched_encoding_names_count` — Create pickle with 3 encodings but 2 names:
   - Load into `EncodingCache`
   - Verify `is_loaded()` returns `False` (validation rejects mismatch)
   - Verify previous valid cache state is preserved (not corrupted)

3. `test_corrupted_pickle_file` — Create a file with random bytes:
   - Load into `EncodingCache`
   - Verify `is_loaded()` returns `False`
   - Verify no exception propagates to the caller

4. `test_nan_encoding_handling` — Create an encoding with `NaN` values:
   - Call `FaceRecognizer.identify_optimized()` with `np.array([float('nan')] * 128)`
   - Verify returns `(UNKNOWN_LABEL, 0.0)` without crash

5. `test_single_registered_face` — Create encoding file with exactly 1 face:
   - Verify recognition works with a single-person database
   - Verify confidence calculation doesn't divide by zero

### Part B: Frame Edge Cases (~4 tests)

6. `test_zero_size_frame` — Pass `np.empty((0, 0, 3), dtype=np.uint8)` to `FaceDetector.detect_faces()`:
   - Verify returns empty list, no crash

7. `test_none_frame_detection` — Pass `None` to `FaceDetector.detect_faces()`:
   - Verify returns empty list (existing behavior, verify it still works)

8. `test_very_large_frame` — Pass `np.zeros((4000, 4000, 3), dtype=np.uint8)`:
   - Verify detection completes without memory error
   - (May find 0 faces, but should not crash)

9. `test_grayscale_frame` — Pass a 2D grayscale frame `(480, 640)` instead of 3-channel:
   - Verify graceful handling (error or automatic conversion, not crash)

### Part C: Recognition Behavior Edge Cases (~4 tests)

10. `test_zero_face_locations_processing` — Pass empty `face_locations = []` through recognition loop:
    - Verify no list index errors
    - Verify face_names, face_confidences, face_statuses remain empty

11. `test_confidence_bounds` — Test with distance = 0.0 (perfect match):
    - Verify confidence doesn't exceed 99% (the formula: `75 + (100 * 0.24) = 99`)

12. `test_confidence_at_tolerance_boundary` — Test with distance = tolerance (0.6):
    - Verify confidence is exactly 75% (the formula: `75 + (0 * 0.24) = 75`)

13. `test_unknown_flood_no_memory_growth` — Simulate 200 consecutive unknown detections through `AttendanceManager`:
    - Verify `unknown_streak` counter increments correctly
    - Verify alert fires at threshold
    - Verify no memory growth (no accumulating data structures)

### Part D: Concurrency Edge Cases (~2 tests)

14. `test_concurrent_api_dispatches` — Dispatch 10 simultaneous API calls:
    - Verify no thread race conditions
    - Verify all results are eventually retrievable
    - Verify `_pending` set is empty after all complete

15. `test_cooldown_boundary_precision` — Set cooldown to 0.05 minutes (3 seconds):
    - Verify attendance at exactly 3 seconds after verification
    - Verify deterministic behavior at the boundary

## Test Structure

```python
import pytest
import numpy as np
import pickle
import tempfile
import os, sys, time
from pathlib import Path
from unittest.mock import MagicMock, patch

ai_module_path = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
if str(ai_module_path) not in sys.path:
    sys.path.insert(0, str(ai_module_path))

from optimization import EncodingCache
from utils import FaceDetector, FaceRecognizer, EncodingManager, AttendanceManager
from config import UNKNOWN_LABEL
```

## Dependencies
- Existing modules: `optimization.py`, `utils.py`, `config.py`
- Step 2 (error handling concepts for graceful failure verification)

## Files Created
- `ai_module/tests/test_edge_cases.py`

## Expected Outcome
15 passing pytest tests that prove the system handles every edge case gracefully. No crashes, no unhandled exceptions, no memory leaks. Running `pytest tests/test_edge_cases.py -v` produces all green results.
