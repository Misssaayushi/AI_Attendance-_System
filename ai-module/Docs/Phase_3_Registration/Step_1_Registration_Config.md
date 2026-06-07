# Step 1: Registration Configuration

## Objective
Extend `config.py` with all settings needed for the registration pipeline so that capture behavior, quality thresholds, and storage paths are controlled from one place.

## Tasks
- Add `CAPTURE_SAMPLE_COUNT` (20) — number of face samples per student.
- Add `CAPTURE_INTERVAL` (0.5) — seconds between captures.
- Add `CAPTURE_TIMEOUT` (60) — max seconds before auto-abort.
- Add `MIN_FACE_SIZE` (100) — minimum bounding box dimension in pixels.
- Add `BLUR_THRESHOLD` (100) — Laplacian variance below this = blurry.
- Add `BRIGHTNESS_MIN` (40) and `BRIGHTNESS_MAX` (250) — acceptable lighting range.
- Add `IMAGE_QUALITY` (90) — JPEG compression quality for saved samples.

## Expected Outcome
A single config section that controls every aspect of the registration behavior.
