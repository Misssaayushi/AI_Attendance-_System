# Step 1: Optimization Configuration

## Objective
Add all Phase 7 performance tuning settings to `ai_module/config.py` so that every optimization component reads from a single centralized location.

## Why This Step Comes First
Every subsequent step (encoding cache, FPS tracker, frame optimizer, API dispatcher) depends on configuration values. Centralizing them prevents hardcoded magic numbers scattered across optimization modules.

## Tasks

1. Add FPS and processing interval settings:
   - `TARGET_FPS = 20` — target frames per second for adaptive tuning
   - `MIN_PROCESS_INTERVAL = 3` — minimum frames between processing
   - `MAX_PROCESS_INTERVAL = 15` — maximum frames between processing
   - `ENABLE_ADAPTIVE_INTERVAL = True` — toggle adaptive vs. fixed interval

2. Add frame optimization settings:
   - `FACE_CROP_PADDING = 30` — pixels of context around face for crop-then-encode
   - Update `FRAME_RESIZE_SCALE` from `0.20` to `0.25` — better small-face detection

3. Add encoding cache settings:
   - `ENCODING_RELOAD_CHECK_SECONDS = 30` — how often to check for file changes
   - `ENCODING_CACHE_ENABLED = True` — toggle singleton cache

4. Add async API settings:
   - `API_DISPATCH_ASYNC = True` — toggle non-blocking API calls

5. Add performance monitoring settings:
   - `ENABLE_FPS_OVERLAY = True` — show FPS on video feed in debug mode
   - `PERF_TRACKER_WINDOW = 30` — rolling average window (frames)
   - `API_FEEDBACK_CLEANUP_INTERVAL = 100` — frames between memory cleanup

6. Add benchmark settings:
   - `BENCHMARK_REPORT_DIR = BASE_DIR / "reports"` — output directory for reports
   - Ensure `BENCHMARK_REPORT_DIR` is created alongside other directories

## Dependencies
- None. This is the foundation step.

## Files Modified
- `ai_module/config.py`

## Expected Outcome
`config.py` contains all Phase 7 settings with sensible defaults. No other file needs modification for this step. All subsequent optimization steps will import from this centralized config.
