# Step 7: Recognition Pipeline Rewrite

## Objective
Rewrite the `start_recognition()` function in `recognize_faces.py` to integrate all Phase 7 optimization components: `EncodingCache`, `PerformanceTracker`, `FrameOptimizer`, and `APIDispatcher`.

## Why This Step
This is the integration step where all individual optimization components come together. The current recognition loop is functional but unoptimized. The rewrite preserves all Phase 4–6 behavior (detection → recognition → verification → API transmission → overlay) while making it significantly faster and more efficient.

## Tasks

### 7.1 — Replace Component Initialization

**Current:**
```python
manager = EncodingManager(encoding_file=ENCODING_FILE)
recognizer = FaceRecognizer(encoding_manager=manager, tolerance=RECOGNITION_TOLERANCE)
```

**Optimized:**
```python
cache = EncodingCache.get_instance()
cache.load(ENCODING_FILE)
recognizer = FaceRecognizer(encoding_manager=manager, tolerance=RECOGNITION_TOLERANCE)
frame_optimizer = FrameOptimizer(padding=FACE_CROP_PADDING)
perf_tracker = PerformanceTracker()
api_dispatcher = APIDispatcher()
```

### 7.2 — Integrate Adaptive Frame Skipping

**Current:** Fixed `RECOGNITION_PROCESS_INTERVAL = 10`.

**Optimized:**
```python
interval = perf_tracker.get_recommended_interval()
if frame_count % interval == 0:
    # Process this frame
```

### 7.3 — Integrate Crop-Then-Encode

**Current:** Full-frame encoding via `recognizer.identify(frame, face_loc)`.

**Optimized:**
```python
rgb_frame = frame_optimizer.prepare_frame(frame)
# Detection still uses resized frame (existing FaceDetector)
# But encoding uses cropped regions:
encoding = frame_optimizer.generate_encoding(rgb_frame, face_loc)
if encoding is not None:
    name, confidence = recognizer.identify_optimized(encoding)
```

### 7.4 — Integrate Non-Blocking API Dispatch

**Current:** Synchronous call blocks the loop.

**Optimized:**
```python
if verified and name != UNKNOWN_LABEL:
    api_dispatcher.dispatch(api_service, student_id, name, confidence)

# Check for completed results (non-blocking)
completed, response = api_dispatcher.get_result(student_id)
if completed:
    api_status, api_color = _resolve_api_feedback(response)
```

### 7.5 — Integrate FPS Tracking and Overlay

Add `perf_tracker.tick()` at the start of each frame. Replace the static header with dynamic performance info when `ENABLE_FPS_OVERLAY` is True:

```python
perf_tracker.tick()

# Replace static overlay with dynamic FPS info
if ENABLE_FPS_OVERLAY and DEBUG_MODE:
    FrameUtils.add_text_overlay(frame, perf_tracker.get_status_string(), position=(10, 30))
```

### 7.6 — Add Periodic Memory Cleanup

Every `API_FEEDBACK_CLEANUP_INTERVAL` frames, clean up expired entries:

```python
if frame_count % API_FEEDBACK_CLEANUP_INTERVAL == 0:
    # Clean expired API feedback
    now = time.time()
    expired_keys = [k for k, v in recent_api_feedback.items() if v["expires_at"] < now]
    for k in expired_keys:
        del recent_api_feedback[k]
    
    # Clean expired dispatcher results
    api_dispatcher.collect_expired(API_FEEDBACK_DISPLAY_SECONDS)
    
    # Check for encoding file changes
    cache.reload_if_changed()
```

### 7.7 — Add Frame Counter Reset

Prevent unbounded integer growth:
```python
frame_count = (frame_count + 1) % 1_000_000
```

### 7.8 — Improve Webcam Retry Logic

**Current:** Single frame failure exits the loop.

**Optimized:**
```python
ret, frame = cam.get_frame()
if not ret:
    retry_count += 1
    if retry_count >= 3:
        logger.error("Webcam failed after 3 retries. Exiting.")
        break
    time.sleep(0.05)
    continue
retry_count = 0
```

### 7.9 — Add Dispatcher Cleanup to Finally Block

```python
finally:
    if 'api_dispatcher' in locals():
        api_dispatcher.cleanup(timeout=2.0)
    if 'cam' in locals():
        cam.cleanup()
```

## Dependencies
- Step 1 (config values)
- Step 2 (EncodingCache)
- Step 3 (PerformanceTracker)
- Step 4 (FrameOptimizer)
- Step 5 (APIDispatcher)
- Step 6 (utils enhancements — identify_optimized, float scale-back)

## Files Modified
- `ai_module/recognize_faces.py` (major rewrite of `start_recognition()`)

## Expected Outcome
The recognition loop maintains all Phase 4–6 functionality while running measurably faster: higher FPS, no API-induced stuttering, adaptive processing, and proper resource management.
