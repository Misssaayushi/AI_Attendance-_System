# Step 6: Recognition Analytics

## Objective
Extend the `ActivityMonitor` class (created in Step 5) with analytics computation methods and session report generation. This provides quantitative metrics about recognition performance and generates a formatted summary report on session exit.

## Why This Step
Analytics are built on top of the activity data collected in Step 5. Separating analytics from raw event logging keeps Step 5 focused and this step purely additive. The session report is the "deliverable" a professor or evaluator can review after a demo.

## Tasks

### Part A: Analytics Computation Methods

Add the following methods to `ActivityMonitor`:

1. `get_recognition_rate() → float`:
   - Returns `(successful_recognitions / total_recognitions) * 100`
   - Returns 0.0 if no recognitions have occurred
   - Successful = identified a known person (not Unknown)

2. `get_unknown_rate() → float`:
   - Returns `(unknown_detections / (total_recognitions + unknown_detections)) * 100`
   - Returns 0.0 if no detections have occurred

3. `get_avg_confidence() → float`:
   - Returns the running average confidence score from `SessionStats`
   - Only includes known person recognitions (excludes unknowns at 0.0%)

4. `get_fps_stats(perf_tracker) → dict`:
   - Accepts a `PerformanceTracker` instance
   - Returns dictionary with: `current_fps`, `avg_fps`, `frame_time_ms`, `processing_interval`
   - Delegates to `PerformanceTracker` methods

5. `get_analytics_summary(perf_tracker=None) → dict`:
   - Combines all analytics into a single dictionary for HUD display
   - Includes:
     - `session_duration_seconds` — elapsed time since session start
     - `session_duration_formatted` — "HH:MM:SS" string
     - `total_recognitions`
     - `successful_recognitions`
     - `recognition_rate_pct`
     - `unknown_detections`
     - `unknown_rate_pct`
     - `unique_students_count`
     - `avg_confidence`
     - `peak_confidence`
     - `cooldown_blocks`
     - `security_flags`
     - `alerts_triggered`
     - FPS stats (if `perf_tracker` provided)

### Part B: Session Report Generation

6. `export_session_report(output_dir=None, perf_tracker=None) → str`:
   - Generates a formatted text report file
   - Default output dir: `ANALYTICS_REPORT_DIR` from config
   - Filename: `session_report_{YYYYMMDD_HHMMSS}.txt`
   - Returns the file path as string

   Report format:
   ```
   ═══════════════════════════════════════════════════════
      AI ATTENDANCE SYSTEM — SESSION REPORT
   ═══════════════════════════════════════════════════════
   Generated:       2026-06-01 09:45:00
   Session Duration: 00:45:12

   ── Recognition Statistics ─────────────────────────────
   Total Face Detections:      312
   Successful Recognitions:    287 (92.0%)
   Unknown Detections:          25 (8.0%)
   Unique Students Verified:    18
   Average Confidence:          89.4%
   Peak Confidence:             97.2%

   ── Attendance Summary ─────────────────────────────────
   Students Verified:           18
   Cooldown Blocks:             42
   Duplicate Attempts:          42

   ── Security Summary ───────────────────────────────────
   Unknown Alerts Triggered:     3
   Security Flags:               0

   ── Performance Metrics ────────────────────────────────
   Average FPS:                 20.1
   Total Frames Processed:      54,144
   Avg Frame Time:              12.4 ms

   ── Verified Students ──────────────────────────────────
   1. 101_John_Doe
   2. 102_Jane_Smith
   3. 103_Bob_Wilson
   ...

   ═══════════════════════════════════════════════════════
   ```

7. `_format_duration(seconds) → str`:
   - Helper to format seconds into "HH:MM:SS"
   - Example: 2712.5 → "00:45:12"

### Part C: Auto-Report on Exit

8. The `cleanup()` method (from Step 5) is extended:
   - If `ANALYTICS_SESSION_REPORT_ON_EXIT` is True:
     - Call `export_session_report()` before closing file handle
     - Log the report file path

## Design Details

### Running Average Confidence
- Uses incremental mean formula: `new_avg = old_avg + (new_value - old_avg) / count`
- No array storage needed — O(1) memory for the running average
- Updated in `log_recognition()` only for known persons

### Report File Location
- Uses the existing `reports/` directory (already created by Phase 7 benchmarks)
- Filename pattern matches existing convention: `session_report_{timestamp}.txt`

### Performance Impact
- Analytics methods are simple arithmetic on pre-computed `SessionStats` fields
- No expensive iteration over event buffers
- `get_analytics_summary()` is designed to be called every frame for HUD update — must be < 0.1ms

## Dependencies
- Step 5 (ActivityMonitor base class, SessionStats, ActivityEvent)
- Step 1 (config values: `ANALYTICS_*`)

## Files Modified
- `ai_module/activity_monitor.py` (extend existing class from Step 5)

## Expected Outcome
The `ActivityMonitor` can now produce quantitative analytics and a formatted session report. The analytics summary is fast enough to be called every frame for the system HUD. On session exit, a professional report file is generated that can be shown to evaluators as evidence of system performance.
