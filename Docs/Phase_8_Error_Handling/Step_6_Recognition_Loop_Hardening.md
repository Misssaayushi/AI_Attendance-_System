# Step 6: Recognition Loop Hardening

## Objective
Rewrite the main recognition loop in `recognize_faces.py` to integrate all Phase 8 error handling components — per-stage try/except blocks, frame quality gating, webcam recovery, graceful degradation on empty encodings, health monitoring, and an optional debug overlay panel.

## Why This Step
This is the most critical step in Phase 8. The current recognition loop (`start_recognition()`) has a single top-level try/except that catches everything. If any individual stage fails (detection, encoding, comparison, API dispatch, overlay rendering), the entire loop crashes. This step wraps each stage individually so failures are isolated and the loop continues.

## Tasks

### Part A: Per-Stage Error Isolation

1. Wrap each pipeline stage in its own try/except block:
   - **Frame Read Stage**: Catch camera failures → trigger recovery
   - **Quality Gate Stage**: Catch quality check failures → skip frame gracefully
   - **Detection Stage**: Catch face detection errors → skip recognition for this frame
   - **Encoding Stage**: Catch encoding generation errors → mark face as Unknown
   - **Comparison Stage**: Catch comparison errors → mark face as Unknown
   - **API Dispatch Stage**: Catch API failures → log error, don't crash
   - **Overlay Render Stage**: Catch drawing errors → show minimal frame

2. Each stage catch block:
   - Records the error to `ErrorTracker` with appropriate `ErrorCategory`
   - Logs the error with source context
   - Continues to the next frame (does NOT break the loop)

### Part B: Integrate Frame Quality Gate

3. After reading a frame, run `FrameQualityGate.check_frame()`:
   - If frame fails quality → display warning overlay, skip recognition, continue
   - Only active when `ENABLE_FRAME_QUALITY_GATE` is `True`
   - Quality warning displayed as amber text on the video feed

### Part C: Integrate Webcam Recovery

4. Replace the current 3-retry hardcoded logic with `RecoveryManager`:
   - When `CameraHandler` detects `WEBCAM_FRAME_RETRY_LIMIT` consecutive failures → trigger `recovery_manager.attempt_webcam_reconnect()`
   - During reconnection: display "Reconnecting Camera..." overlay
   - On success: resume recognition loop normally
   - On failure: display "Camera Unavailable" overlay and exit loop

### Part D: Graceful Degradation on Empty Encodings

5. Check `EncodingCache.is_loaded()` before processing:
   - If encodings are not loaded → display "No Encodings Loaded — Register Students First" overlay
   - Continue running the webcam feed (don't crash)
   - Periodically check if encodings become available (via `reload_if_changed()`)

### Part E: Health Monitoring Integration

6. Integrate `ErrorTracker` for system health:
   - Create error tracker instance at startup
   - Pass to each stage for error recording
   - Every `HEALTH_CHECK_INTERVAL_FRAMES` frames: check `error_tracker.is_healthy()`
   - If unhealthy: log warning, optionally increase processing interval to reduce load

### Part F: Debug Overlay Panel

7. When `ENABLE_DEBUG_OVERLAY and DEBUG_MODE`, draw a compact health panel:
   - Background: semi-transparent dark rectangle in bottom-left corner
   - Content (5 lines):
     ```
     Health: HEALTHY / DEGRADED
     Errors: 2/min | Recoveries: 1
     FPS: 22.3 | FrameTime: 45ms
     Encodings: 60 loaded
     Quality: 95% pass rate
     ```
   - Colors: Green text for healthy, amber for degraded, red for unhealthy

## Design Details

### Pipeline Stage Map
```
Frame Loop Iteration
    │
    ├── [1] Frame Read Stage (try/except)
    │   ├── cam.get_frame()
    │   └── on failure → recovery_manager.attempt_webcam_reconnect()
    │
    ├── [2] Quality Gate Stage (try/except)
    │   ├── quality_gate.check_frame(frame)
    │   └── on failure → display warning, skip to next frame
    │
    ├── [3] Detection Stage (try/except)
    │   ├── detector.detect_faces(frame)
    │   └── on failure → skip recognition, show frame without boxes
    │
    ├── [4] Encoding + Comparison Stage (try/except, per face)
    │   ├── frame_optimizer.generate_encoding()
    │   ├── recognizer.identify_optimized()
    │   └── on failure → mark face as Unknown
    │
    ├── [5] Verification + API Stage (try/except, per face)
    │   ├── attendance_manager.verify_attendance()
    │   ├── api_dispatcher.dispatch()
    │   └── on failure → log error, skip API for this face
    │
    ├── [6] Overlay Render Stage (try/except)
    │   ├── draw face boxes, labels, legend
    │   ├── draw debug overlay (if enabled)
    │   └── on failure → show raw frame
    │
    └── [7] Cleanup + Health Check
        ├── periodic cache reload check
        ├── periodic API feedback cleanup
        └── periodic health evaluation
```

### Imports to Add
```python
from error_handler import ErrorTracker, RecoveryManager, FrameQualityGate, ErrorCategory, SystemError
```

### New Config Imports
```python
from config import (
    ENABLE_FRAME_QUALITY_GATE, ENABLE_DEBUG_OVERLAY,
    HEALTH_CHECK_INTERVAL_FRAMES, WEBCAM_FRAME_RETRY_LIMIT
)
```

## Dependencies
- Step 1 (config values)
- Step 2 (ErrorTracker, ErrorCategory, SystemError)
- Step 4 (RecoveryManager, enhanced CameraHandler)
- Step 5 (FrameQualityGate)

## Files Modified
- `ai_module/recognize_faces.py` (major rewrite of `start_recognition()`)

## Expected Outcome
The recognition loop is fully hardened:
- No single stage failure can crash the loop
- Frame quality is validated before expensive processing
- Webcam disconnects trigger automatic recovery
- Empty encodings show guidance instead of crashing
- System health is monitored and displayed in debug mode
- The system runs stably for extended periods under real-world conditions
