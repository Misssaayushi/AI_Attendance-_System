# Step 5: Frame Quality Gate

## Objective
Create `FrameQualityGate` in `error_handler.py` — a lightweight pre-recognition filter that rejects blurry, too-dark, or overexposed frames before they reach the expensive face encoding pipeline.

## Why This Step
Currently, every frame — regardless of quality — goes through the full face detection → encoding → comparison pipeline. This wastes CPU time and produces unreliable recognition results:
- **Blurry frames** generate noisy encodings that cause flickering recognition
- **Dark frames** fail face detection silently, burning cycles for nothing
- **Overexposed frames** wash out facial features, reducing confidence

The `FrameQualityGate` runs in ~0.5ms (vs. ~30ms for face encoding), saving significant compute on bad frames.

## Tasks

1. Add `FrameQualityGate` class to `error_handler.py`:

2. Implement `check_frame(frame) -> (bool, str)`:
   - Returns `(True, "OK")` if the frame passes all quality checks
   - Returns `(False, reason)` if the frame fails, where `reason` is a user-friendly string
   - Handles `None` and empty frames gracefully

3. Implement blur detection:
   - Convert frame to grayscale
   - Calculate Laplacian variance: `cv2.Laplacian(gray, cv2.CV_64F).var()`
   - If variance < `QUALITY_GATE_BLUR_THRESHOLD` → reject with "Frame too blurry"
   - This reuses the same technique as `FaceValidator.is_blurry()` but with a lower threshold (50 vs 100) because recognition can tolerate more blur than registration

4. Implement brightness detection:
   - Convert frame to grayscale (reuse from blur step)
   - Calculate mean pixel intensity: `np.mean(gray)`
   - If mean < `QUALITY_GATE_BRIGHTNESS_MIN` → reject with "Low lighting detected"
   - If mean > `QUALITY_GATE_BRIGHTNESS_MAX` → reject with "Overexposed frame"

5. Implement `get_stats() -> dict`:
   - Track total frames checked, frames passed, frames rejected
   - Track rejection reasons (blur count, dark count, bright count)
   - Calculate pass rate percentage

## Design Details

### FrameQualityGate
```
FrameQualityGate
├── __init__()
├── check_frame(frame) → (bool, str)
├── get_stats() → dict
├── _total_checked: int
├── _total_passed: int
├── _blur_rejections: int
├── _dark_rejections: int
└── _bright_rejections: int
```

### Quality Check Pipeline
```
Frame from webcam
    │
    ├── frame is None or empty?
    │   └── return (False, "Invalid frame")
    │
    ├── Convert to grayscale (one conversion, reused)
    │
    ├── Blur check: Laplacian variance < 50?
    │   └── return (False, "Frame too blurry")
    │
    ├── Brightness check: mean < 30?
    │   └── return (False, "Low lighting detected")
    │
    ├── Brightness check: mean > 245?
    │   └── return (False, "Overexposed frame")
    │
    └── return (True, "OK")
```

### Performance Comparison
| Operation | Time | When Skipped |
|---|---|---|
| Frame Quality Gate | ~0.5 ms | Never (always runs) |
| Face Detection | ~10–20 ms | Skipped on quality failure |
| Face Encoding | ~30–50 ms | Skipped on quality failure |
| Face Comparison | ~1–5 ms | Skipped on quality failure |
| **Total saved per bad frame** | **~40–75 ms** | |

### Integration Point (Step 6)
```python
# In recognize_faces.py main loop:
if ENABLE_FRAME_QUALITY_GATE:
    quality_ok, quality_reason = quality_gate.check_frame(frame)
    if not quality_ok:
        # Display quality warning overlay
        FrameUtils.add_text_overlay(frame, f"Quality: {quality_reason}", ...)
        cam.show_frame("AI Attendance Recognition", frame)
        continue  # Skip recognition, process next frame
```

## Dependencies
- Step 1 (config values: `ENABLE_FRAME_QUALITY_GATE`, `QUALITY_GATE_BLUR_THRESHOLD`, `QUALITY_GATE_BRIGHTNESS_MIN`, `QUALITY_GATE_BRIGHTNESS_MAX`)

## Files Modified (continued from Steps 2 & 4)
- `ai_module/error_handler.py` (add `FrameQualityGate` class)

## Expected Outcome
Bad frames are rejected in ~0.5ms before reaching the expensive face encoding pipeline. The recognition loop displays quality warnings on the video feed instead of producing noisy results. Frame quality statistics are available for diagnostics.
