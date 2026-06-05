# Step 10: Testing & Validation

## Objective
Create a comprehensive test suite `ai_module/tests/test_phase9_features.py` covering all Phase 9 components. Run the full regression suite and validate that Phase 9 features do not degrade FPS or existing functionality.

## Why This Step
Testing is the final step to ensure all Phase 9 features work correctly in isolation and together. The test suite validates that alerts trigger correctly, overlays render without errors, analytics are accurate, and performance impact is within budget.

## Tasks

### Part A: Unknown Alert Tests

1. **test_alert_triggers_after_threshold**:
   - Call `process_unknown()` for `UNKNOWN_ALERT_CONSECUTIVE_FRAMES` times
   - Assert that `AlertEvent` is returned on the threshold frame
   - Assert that `AlertEvent` has valid UUID, timestamp, and consecutive count

2. **test_alert_suppressed_during_cooldown**:
   - Trigger one alert successfully
   - Immediately call `process_unknown()` again for threshold frames
   - Assert that no new alert is returned (cooldown suppression)

3. **test_alert_reset_on_known_person**:
   - Call `process_unknown()` for 3 frames (below threshold)
   - Call `reset()`
   - Call `process_unknown()` for 3 more frames
   - Assert no alert triggered (counter was reset)

4. **test_snapshot_saves_file**:
   - Create a synthetic frame and face location
   - Trigger an alert with snapshots enabled
   - Assert that a `.jpg` file exists in the snapshot directory
   - Clean up created file after test

5. **test_storage_cap_enforced**:
   - Create more snapshots than `UNKNOWN_SNAPSHOT_MAX_STORED`
   - Assert that file count does not exceed the cap
   - Assert that oldest files are deleted first

6. **test_alert_stats_accuracy**:
   - Trigger multiple alerts
   - Call `get_alert_stats()`
   - Assert counts match expected values

### Part B: Overlay Renderer Tests

7. **test_draw_face_overlay_no_exception**:
   - Create a synthetic 640×480 frame
   - Call `draw_face_overlay()` with various state combinations (verified, unknown, cooldown, pending)
   - Assert no exceptions raised

8. **test_confidence_bar_renders**:
   - Create a synthetic frame
   - Call `draw_confidence_bar()` at 0%, 50%, and 100% confidence
   - Assert frame is modified (pixel values changed in bar region)

9. **test_system_hud_renders**:
   - Create a synthetic frame
   - Call `draw_system_hud()` with mock session stats
   - Assert no exceptions and frame dimensions unchanged

10. **test_unknown_warning_banner_renders**:
    - Create a synthetic frame
    - Call `draw_unknown_warning_banner()` with a mock alert event
    - Assert frame is modified in banner region

### Part C: Cooldown Enhancement Tests

11. **test_profile_switching**:
    - Create `AttendanceManager` with default profile
    - Call `set_cooldown_profile("exam")`
    - Assert cooldown_minutes changed to 120

12. **test_remaining_time_calculation**:
    - Verify a student (triggers cooldown)
    - Call `get_cooldown_remaining(student_id)`
    - Assert remaining seconds > 0 and < cooldown_minutes * 60

13. **test_format_cooldown_remaining**:
    - Verify a student
    - Call `format_cooldown_remaining(student_id)`
    - Assert format matches "MM:SS" pattern

14. **test_lock_registry**:
    - Lock a student with `lock_student(student_id, 60)`
    - Assert `is_locked(student_id)` returns True
    - Simulate time passage (mock or short lock)
    - Assert `is_locked(student_id)` returns False after expiry

15. **test_duplicate_attempts_counter**:
    - Verify a student (enters cooldown)
    - Attempt to verify same student again
    - Assert `duplicate_attempts` incremented

### Part D: Activity Monitor Tests

16. **test_log_recognition_updates_stats**:
    - Create `ActivityMonitor`
    - Log 5 recognition events with varying confidence
    - Assert `get_session_stats()` reflects correct counts and avg confidence

17. **test_jsonl_format_valid**:
    - Log several events
    - Call `flush()`
    - Read the JSONL file and parse each line as JSON
    - Assert all lines are valid JSON with expected fields

18. **test_buffer_eviction**:
    - Set `ACTIVITY_LOG_MAX_ENTRIES` to a small value (e.g., 10)
    - Log 15 events
    - Assert in-memory buffer size does not exceed cap

19. **test_session_report_generation**:
    - Log various events
    - Call `export_session_report()`
    - Assert report file exists and contains expected sections

20. **test_cleanup_flushes_buffer**:
    - Log events without manual flush
    - Call `cleanup()`
    - Verify all events are written to JSONL file

### Part E: Security Monitor Tests

21. **test_unknown_threshold_triggers_flag**:
    - Call `track_unknown_detection()` for `SECURITY_REPEATED_UNKNOWN_THRESHOLD` times
    - Assert `is_suspicious()` returns True

22. **test_low_confidence_streak_detection**:
    - Call `track_low_confidence(student_id, 50.0)` for `SECURITY_LOW_CONFIDENCE_STREAK_THRESHOLD` times
    - Assert security flag is raised

23. **test_identity_switch_detection**:
    - Call `track_identity(position_key, "Alice")`
    - Call `track_identity(position_key, "Bob")`
    - Call `track_identity(position_key, "Charlie")`
    - Assert identity switching event logged

24. **test_security_summary_structure**:
    - Trigger various security events
    - Call `get_security_summary()`
    - Assert all expected keys present in returned dict

25. **test_counters_reset**:
    - Trigger flags, then call `reset_unknown_counter()`
    - Assert unknown counter is zero

### Part F: Performance Validation Tests

26. **test_overlay_rendering_performance**:
    - Create 100 synthetic frames
    - Time overlay rendering per frame
    - Assert average time < 2ms per face

27. **test_analytics_tracking_performance**:
    - Time 1000 calls to `log_recognition()` and `get_analytics_summary()`
    - Assert average time < 0.5ms per call

28. **test_memory_stability**:
    - Run 1000 iterations of: log event + render overlay
    - Monitor memory using `tracemalloc`
    - Assert memory growth < 1 MB over 1000 iterations

### Part G: Integration Smoke Test

29. **test_all_components_initialize**:
    - Import and instantiate all Phase 9 components
    - Assert no import errors or initialization failures

30. **test_full_pipeline_synthetic**:
    - Create synthetic frame
    - Run through: detection → recognition → alert check → activity log → overlay render
    - Assert no exceptions throughout the full pipeline

## Design Details

### Test Fixtures
- Use `pytest` fixtures for:
  - `synthetic_frame` — 640×480 random numpy array
  - `sample_face_location` — `(100, 300, 300, 100)` standard face box
  - `temp_dir` — temporary directory for snapshot and log file tests (cleaned up after)

### Test Isolation
- Each test creates its own component instances (no shared state)
- File-based tests use `tmp_path` pytest fixture for automatic cleanup
- Config values are NOT mocked — tests use actual config defaults

### Running Tests
```bash
# Run Phase 9 tests only
python -m pytest tests/test_phase9_features.py -v

# Run with performance timing
python -m pytest tests/test_phase9_features.py -v --durations=10

# Run full regression suite
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ -v --cov=. --cov-report=term-missing
```

## Dependencies
- Steps 1–9 (all Phase 9 components must be implemented)

## Files Created
- `ai_module/tests/test_phase9_features.py`

## Expected Outcome
A comprehensive test suite with ~30 tests covering all Phase 9 components. All tests pass. The full regression suite (including Phase 7 and Phase 8 tests) shows no failures. Performance validation confirms that Phase 9 features stay within the ~2–3ms per-frame budget. The system is verified as demo-ready.
