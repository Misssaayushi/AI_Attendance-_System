# Step 1: Phase 9 Configuration

## Objective
Add all Phase 9 advanced feature settings to `ai_module/config.py` so that every new component reads from a single centralized location.

## Why This Step Comes First
Every subsequent step (unknown alerts, overlay renderer, activity monitor, security monitor) depends on configuration values. Centralizing them prevents hardcoded magic numbers scattered across new modules and allows easy tuning during demo preparation.

## Tasks

1. Add unknown person alert settings:
   - `UNKNOWN_SNAPSHOTS_DIR = BASE_DIR / "unknown_snapshots"` — directory for unknown face crops
   - `UNKNOWN_ALERT_CONSECUTIVE_FRAMES = 5` — frames before triggering alert
   - `UNKNOWN_ALERT_COOLDOWN_SECONDS = 30` — suppress duplicate alerts within window
   - `UNKNOWN_SNAPSHOT_ENABLED = True` — toggle face crop saving
   - `UNKNOWN_SNAPSHOT_MAX_STORED = 100` — cap disk usage
   - `UNKNOWN_SNAPSHOT_QUALITY = 85` — JPEG quality for snapshots

2. Add enhanced overlay settings:
   - `OVERLAY_SHOW_CONFIDENCE_BAR = True` — visual confidence meter
   - `OVERLAY_SHOW_TIMESTAMP = True` — timestamp on face box
   - `OVERLAY_ANIMATION_ENABLED = True` — animated border pulse on verify
   - `OVERLAY_BORDER_THICKNESS = 2` — face box line width
   - `OVERLAY_FONT_SCALE = 0.55` — text size multiplier

3. Add cooldown enhancement settings:
   - `COOLDOWN_DISPLAY_REMAINING = True` — show "Next scan in X:XX"
   - `COOLDOWN_LOCK_VISUAL_ENABLED = True` — lock icon on cooldown faces
   - `COOLDOWN_CONFIGURABLE_PROFILES` — dict with named cooldown durations (lecture: 30, lab: 60, exam: 120 minutes)
   - `ACTIVE_COOLDOWN_PROFILE = "lecture"` — current active profile

4. Add activity monitoring settings:
   - `ACTIVITY_LOG_FILE = LOGS_DIR / "activity_log.jsonl"` — JSONL activity log path
   - `ACTIVITY_LOG_MAX_ENTRIES = 10000` — rotate after N entries
   - `ACTIVITY_LOG_FLUSH_INTERVAL = 10` — flush to disk every N events

5. Add analytics settings:
   - `ANALYTICS_ENABLED = True` — master toggle for analytics
   - `ANALYTICS_REPORT_DIR = BASE_DIR / "reports"` — reuses existing reports directory
   - `ANALYTICS_SESSION_REPORT_ON_EXIT = True` — auto-generate report on quit

6. Add security monitoring settings:
   - `SECURITY_REPEATED_UNKNOWN_THRESHOLD = 10` — flag as suspicious after N unknowns
   - `SECURITY_LOW_CONFIDENCE_STREAK_THRESHOLD = 5` — flag unstable recognition
   - `SECURITY_ALERT_LOG_FILE = LOGS_DIR / "security_alerts.log"` — dedicated security log

7. Add new directories to the creation loop:
   - `UNKNOWN_SNAPSHOTS_DIR` must be created alongside existing directories

## Configuration Rationale

| Setting | Value | Reasoning |
|---|---|---|
| `UNKNOWN_ALERT_CONSECUTIVE_FRAMES` | 5 | Avoids false alerts from single misrecognition frames, requires sustained unknown presence |
| `UNKNOWN_ALERT_COOLDOWN_SECONDS` | 30 | Prevents log flooding — one alert per 30s for the same unknown person is sufficient |
| `UNKNOWN_SNAPSHOT_MAX_STORED` | 100 | ~100 JPEG crops ≈ 5–10 MB disk — safe for demo environments |
| `COOLDOWN_CONFIGURABLE_PROFILES` | 3 profiles | Covers common university scenarios without over-engineering |
| `ACTIVITY_LOG_FLUSH_INTERVAL` | 10 | Batched writes reduce I/O overhead while keeping near-real-time persistence |
| `SECURITY_REPEATED_UNKNOWN_THRESHOLD` | 10 | High enough to avoid false flags from brief visitor walkbys |

## Dependencies
- None. This is the foundation step.

## Files Modified
- `ai_module/config.py`

## Expected Outcome
`config.py` contains all Phase 9 settings with sensible defaults appended after the existing Phase 8 block. The `UNKNOWN_SNAPSHOTS_DIR` directory is auto-created at import time. No other file needs modification for this step. All subsequent Phase 9 steps will import from this centralized config.
