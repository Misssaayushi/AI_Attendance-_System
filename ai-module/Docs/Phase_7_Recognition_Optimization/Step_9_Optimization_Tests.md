# Step 9: Optimization Test Suite

## Objective
Create comprehensive unit and integration tests for all Phase 7 optimization components in `test_optimization.py` and `test_benchmark.py`.

## Why This Step
Every optimization must be validated to ensure it works correctly and doesn't break existing functionality. Tests also serve as regression guards for future changes.

## Tasks

### 9.1 — Create `ai_module/tests/test_optimization.py`

#### EncodingCache Tests

1. **`test_singleton_identity`** — Create two instances via `get_instance()`. Assert they are the same object (`is` identity).

2. **`test_load_valid_encoding`** — Create a temporary pickle file with valid encoding data. Load it via `EncodingCache`. Assert encoding count and names match.

3. **`test_load_missing_file`** — Attempt to load a non-existent file. Assert cache remains empty, no exception raised.

4. **`test_load_corrupted_file`** — Create a pickle file with invalid structure (missing keys). Assert cache handles it gracefully, logs error.

5. **`test_reload_on_file_change`** — Load a file, modify it (add new encoding), call `reload_if_changed()`. Assert new data is loaded.

6. **`test_no_reload_when_unchanged`** — Load a file, call `reload_if_changed()` without modifying. Assert no reload occurs (check load count).

7. **`test_numpy_matrix_shape`** — Load N encodings. Assert returned matrix has shape `(N, 128)`.

8. **`test_get_stats_returns_expected_keys`** — After loading, assert `get_stats()` contains keys: `count`, `file_size`, `load_time_ms`, `memory_bytes`.

#### PerformanceTracker Tests

9. **`test_fps_calculation`** — Feed known intervals (0.05s = 20 FPS). Assert `get_fps()` returns ~20.

10. **`test_rolling_average`** — Feed a mix of fast and slow frames. Assert `get_avg_fps()` returns the correct average.

11. **`test_adaptive_interval_decrease`** — Simulate high FPS (>TARGET_FPS * 1.2). Assert recommended interval decreases.

12. **`test_adaptive_interval_increase`** — Simulate low FPS (<TARGET_FPS * 0.8). Assert recommended interval increases.

13. **`test_adaptive_interval_bounds`** — Assert interval never goes below `MIN_PROCESS_INTERVAL` or above `MAX_PROCESS_INTERVAL`.

14. **`test_status_string_format`** — Assert `get_status_string()` contains "FPS" and "Avg" substrings.

#### FrameOptimizer Tests

15. **`test_crop_within_bounds`** — Create a 480×640 frame, set face location in center. Assert crop region is within frame bounds.

16. **`test_crop_at_edge`** — Set face location at frame edge (e.g., top=0, left=0). Assert coordinates are clamped, no out-of-bounds error.

17. **`test_prepare_frame_returns_rgb`** — Pass a BGR frame. Assert returned frame has RGB channel order (check a known pixel value).

18. **`test_generate_encoding_returns_128d`** — Use a real face image (or mock). Assert returned encoding has 128 dimensions.

#### APIDispatcher Tests

19. **`test_dispatch_does_not_block`** — Dispatch a call with a mock API service that sleeps 1 second. Assert dispatch returns in <50ms.

20. **`test_result_retrieval`** — Dispatch, wait for completion, call `get_result()`. Assert result is returned.

21. **`test_duplicate_prevention`** — Dispatch for same student_id twice. Assert second dispatch is skipped (is_pending returns True).

22. **`test_collect_expired`** — Add results with expired timestamps. Call `collect_expired()`. Assert expired results are removed.

23. **`test_sync_fallback`** — Set `API_DISPATCH_ASYNC = False`. Assert dispatch runs synchronously and result is immediately available.

### 9.2 — Create `ai_module/tests/test_benchmark.py`

24. **`test_encoding_load_benchmark`** — Run load benchmark. Assert report contains timing data.

25. **`test_large_dataset_simulation`** — Generate synthetic encodings (500 faces). Load into cache. Measure comparison time. Assert it completes in reasonable time (<100ms for 500 comparisons).

26. **`test_memory_usage_measurement`** — Load encodings, get memory stats. Assert values are positive numbers.

27. **`test_report_generation`** — Run full benchmark, generate report. Assert file exists and contains expected sections.

28. **`test_long_session_stability`** — Simulate 1000 frame ticks. Assert FPS tracker doesn't accumulate unbounded data (deque stays at maxlen).

### 9.3 — Verify Existing Tests Still Pass

29. **Run `test_integration.py`** — Assert all Phase 6 integration tests pass without modification.

30. **Run `test_verification.py`** — Assert attendance verification logic is unaffected.

## Test Utilities

Create helper fixtures:
- `create_temp_encoding_file(n_students, n_encodings_per)` — generates synthetic pickle files for testing.
- `create_dummy_frame(height, width)` — creates a random numpy array simulating a camera frame.

## Dependencies
- Steps 2–5 (all optimization classes must be implemented)
- Step 6 (utils enhancements)

## Files Created
- `ai_module/tests/test_optimization.py`
- `ai_module/tests/test_benchmark.py`

## Expected Outcome
Comprehensive test coverage for all optimization components. Tests can be run with `python -m pytest AI_Module/tests/ -v` and should all pass.
