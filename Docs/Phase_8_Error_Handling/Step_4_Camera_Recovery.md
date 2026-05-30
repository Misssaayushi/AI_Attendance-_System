# Step 4: Camera Recovery System

## Objective
Enhance `CameraHandler` in `utils.py` with automatic webcam reconnection and create `RecoveryManager` in `error_handler.py` for managing all recovery workflows with exponential backoff.

## Why This Step
Currently, if the webcam disconnects during a live demo:
- `CameraHandler.__init__` raises a fatal `Exception` → full crash
- The recognition loop has a hardcoded 3-retry limit → exits after 3 frame failures
- There is no reconnection logic → the system must be manually restarted

This is unacceptable for a demo environment where USB cameras can momentarily disconnect.

## Tasks

### Part A: Enhance CameraHandler in utils.py

1. Add `reconnect()` method:
   - Releases the current `cv2.VideoCapture` if it exists
   - Creates a new `cv2.VideoCapture(self.camera_id)`
   - Returns `True` if the new capture opened successfully, `False` otherwise
   - Logs the reconnection attempt and result

2. Add `is_connected` property:
   - Returns `self.cap is not None and self.cap.isOpened()`

3. Add consecutive failure tracking to `get_frame()`:
   - Track consecutive frame-read failures with `self._consecutive_failures` counter
   - Reset counter to 0 on successful frame read
   - When counter reaches `WEBCAM_FRAME_RETRY_LIMIT`, trigger `reconnect()` and reset counter
   - Log warning with failure count on each failure

4. Update `__init__()`:
   - Instead of raising `Exception` on failure, log the error and set `self.cap = None`
   - The recognition loop will detect `is_connected == False` and trigger recovery

### Part B: Create RecoveryManager in error_handler.py

1. Add `RecoveryManager` class to `error_handler.py`:

2. Implement `attempt_webcam_reconnect(camera_handler) -> bool`:
   - Uses exponential backoff: delay starts at `WEBCAM_RECONNECT_BASE_DELAY`, doubles each attempt
   - Caps at `WEBCAM_RECONNECT_MAX_DELAY`
   - Max attempts: `WEBCAM_MAX_RECONNECT_ATTEMPTS`
   - Each attempt: calls `camera_handler.reconnect()`
   - Logs each attempt with delay and attempt number
   - Returns `True` if any attempt succeeds, `False` if all fail
   - Records success/failure in internal stats

3. Implement `attempt_encoding_reload(encoding_cache, path) -> bool`:
   - Attempts to reload the encoding file
   - If the file is corrupted, logs error and returns `False`
   - If the file is missing, logs warning and returns `False`
   - On success, returns `True`
   - Does not crash regardless of file state

4. Implement `get_recovery_stats() -> dict`:
   - Returns dictionary with:
     - `webcam_recovery_attempts: int`
     - `webcam_recovery_successes: int`
     - `encoding_reload_attempts: int`
     - `encoding_reload_successes: int`

## Design Details

### Exponential Backoff Sequence
```
Attempt 1: wait 1.0s → try reconnect
Attempt 2: wait 2.0s → try reconnect
Attempt 3: wait 4.0s → try reconnect
Attempt 4: wait 8.0s → try reconnect
Attempt 5: wait 16.0s → try reconnect (capped at max delay)
→ All failed: return False, system shows "Camera Unavailable" overlay
```

### CameraHandler Enhancement
```
CameraHandler
├── __init__(camera_id) — no longer raises on failure
├── get_frame() → (ret, frame) — tracks consecutive failures
├── reconnect() → bool — releases and re-opens VideoCapture
├── is_connected → bool — property checking cap status
├── show_frame(window_name, frame) — unchanged
├── cleanup() — unchanged
└── _consecutive_failures: int — internal counter
```

### RecoveryManager
```
RecoveryManager
├── attempt_webcam_reconnect(camera_handler) → bool
├── attempt_encoding_reload(cache, path) → bool
├── get_recovery_stats() → dict
├── _webcam_attempts: int
├── _webcam_successes: int
├── _encoding_attempts: int
└── _encoding_successes: int
```

## Recovery Flow in Recognition Loop

```
get_frame() returns (False, None)
    │
    ├── _consecutive_failures += 1
    │
    ├── if failures < WEBCAM_FRAME_RETRY_LIMIT:
    │   └── continue (skip this frame, try next)
    │
    └── if failures >= WEBCAM_FRAME_RETRY_LIMIT:
        ├── log: "Triggering webcam recovery..."
        ├── call recovery_manager.attempt_webcam_reconnect(cam)
        │   ├── success → reset counter, continue loop
        │   └── failure → display "Camera Unavailable" overlay, break loop
        └── reset _consecutive_failures
```

## Dependencies
- Step 1 (config values: `WEBCAM_MAX_RECONNECT_ATTEMPTS`, `WEBCAM_RECONNECT_BASE_DELAY`, `WEBCAM_RECONNECT_MAX_DELAY`, `WEBCAM_FRAME_RETRY_LIMIT`)
- Step 2 (ErrorTracker for logging recovery events)

## Files Modified
- `ai_module/utils.py` (enhance `CameraHandler` class)

## Files Modified (continued from Step 2)
- `ai_module/error_handler.py` (add `RecoveryManager` class)

## Expected Outcome
The webcam can disconnect and reconnect without requiring a system restart. The system attempts reconnection with exponential backoff and displays clear status messages during recovery. Encoding files can be reloaded safely even if corrupted.
