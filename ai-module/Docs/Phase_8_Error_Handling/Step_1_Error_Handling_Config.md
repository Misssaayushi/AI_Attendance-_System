# Step 1: Error Handling Configuration

## Objective
Add all Phase 8 error handling, recovery, and testing settings to `ai_module/config.py` so that every stability component reads from a single centralized location.

## Why This Step Comes First
Every subsequent step (error tracker, recovery manager, frame quality gate, diagnostics) depends on configuration values. Centralizing them prevents hardcoded magic numbers scattered across error handling modules.

## Tasks

1. Add webcam recovery settings:
   - `WEBCAM_MAX_RECONNECT_ATTEMPTS = 5` — max reconnection tries before giving up
   - `WEBCAM_RECONNECT_BASE_DELAY = 1.0` — initial delay in seconds, doubles each attempt
   - `WEBCAM_RECONNECT_MAX_DELAY = 16.0` — cap on exponential backoff delay
   - `WEBCAM_FRAME_RETRY_LIMIT = 10` — consecutive frame-read failures before triggering reconnect

2. Add frame quality gating settings:
   - `ENABLE_FRAME_QUALITY_GATE = True` — toggle pre-recognition quality check
   - `QUALITY_GATE_BLUR_THRESHOLD = 50.0` — Laplacian variance below this = too blurry
   - `QUALITY_GATE_BRIGHTNESS_MIN = 30` — average pixel intensity below this = too dark
   - `QUALITY_GATE_BRIGHTNESS_MAX = 245` — average pixel intensity above this = overexposed

3. Add error monitoring settings:
   - `ERROR_RATE_WINDOW_SECONDS = 60` — sliding window for error rate calculation
   - `ERROR_RATE_THRESHOLD = 10` — errors per window that triggers a health warning
   - `HEALTH_CHECK_INTERVAL_FRAMES = 100` — frames between system health evaluations

4. Add logging settings:
   - `LOG_ROTATION_MAX_BYTES = 5 * 1024 * 1024` — 5 MB max per log file
   - `LOG_ROTATION_BACKUP_COUNT = 3` — keep 3 rotated backup files
   - `ENABLE_STRUCTURED_LOGGING = True` — use structured log format with event type prefixes

5. Add debug overlay settings:
   - `ENABLE_DEBUG_OVERLAY = True` — show health panel on video feed when `DEBUG_MODE` is active

6. Add memory monitoring settings:
   - `MEMORY_WARNING_THRESHOLD_MB = 500` — warn if Python heap exceeds this value

## Configuration Rationale

| Setting | Value | Reasoning |
|---|---|---|
| `WEBCAM_MAX_RECONNECT_ATTEMPTS` | 5 | Enough for USB glitches, not infinite to prevent hanging |
| `QUALITY_GATE_BLUR_THRESHOLD` | 50.0 | Lower than registration threshold (100) — recognition tolerates more blur |
| `ERROR_RATE_THRESHOLD` | 10 | 10 errors/minute is concerning; 1 error/6 seconds indicates a real problem |
| `LOG_ROTATION_MAX_BYTES` | 5 MB | Keeps 4 files total (current + 3 backups) = 20 MB max disk usage |

## Dependencies
- None. This is the foundation step.

## Files Modified
- `ai_module/config.py`

## Expected Outcome
`config.py` contains all Phase 8 settings with sensible defaults appended after the existing Phase 7 block. No other file needs modification for this step. All subsequent error handling steps will import from this centralized config.
