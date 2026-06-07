# Step 3: Performance Tracker

## Objective
Create a `PerformanceTracker` class in `ai_module/optimization.py` that measures real-time FPS, frame processing time, and provides adaptive processing interval recommendations.

## Why This Step
The current recognition loop has no performance observability. Without FPS measurement, it's impossible to detect degradation, validate optimizations, or adapt behavior to hardware capability. The performance tracker is the foundation for adaptive frame skipping and the FPS overlay.

## Tasks

1. Add `PerformanceTracker` class to `optimization.py`.

2. Implement high-resolution timing:
   - Use `time.perf_counter()` instead of `time.time()` for microsecond-level accuracy.
   - Record timestamp at start of each frame and at end of processing.

3. Implement FPS calculation:
   - `tick()` — called once per frame, records timestamp.
   - `get_fps()` — returns instantaneous FPS (1 / time since last tick).
   - `get_avg_fps()` — returns rolling average FPS over the last N frames.
   - Use a `collections.deque(maxlen=PERF_TRACKER_WINDOW)` to store recent frame times.

4. Implement frame-time measurement:
   - `get_frame_time_ms()` — returns time spent in the last frame in milliseconds.
   - Useful for identifying which frames are slow (detection frames vs. display-only frames).

5. Implement adaptive processing interval:
   - `get_recommended_interval()` — returns the optimal frame skip count based on current FPS.
   - Logic:
     - If `avg_fps > TARGET_FPS * 1.2` → decrease interval (process more often), min = `MIN_PROCESS_INTERVAL`
     - If `avg_fps < TARGET_FPS * 0.8` → increase interval (skip more frames), max = `MAX_PROCESS_INTERVAL`
     - Otherwise → hold current interval
   - Only active when `ENABLE_ADAPTIVE_INTERVAL` is True. Falls back to fixed `RECOGNITION_PROCESS_INTERVAL` otherwise.

6. Implement diagnostic output:
   - `get_status_string()` — returns formatted string like: `"FPS: 24 | Avg: 22.3 | Interval: 5 | FrameTime: 42ms"`
   - Used for the FPS overlay and debug logging.

## Design Details

```
PerformanceTracker
├── _frame_times: deque (rolling window)
├── _last_tick: float
├── _current_interval: int
├── tick() → None
├── get_fps() → float
├── get_avg_fps() → float
├── get_frame_time_ms() → float
├── get_recommended_interval() → int
└── get_status_string() → str
```

## Dependencies
- Step 1 (config values: `TARGET_FPS`, `MIN_PROCESS_INTERVAL`, `MAX_PROCESS_INTERVAL`, `ENABLE_ADAPTIVE_INTERVAL`, `PERF_TRACKER_WINDOW`)

## Files Modified
- `ai_module/optimization.py` (add `PerformanceTracker` class)

## Expected Outcome
A lightweight tracker that provides real-time FPS metrics and dynamically adjusts the frame processing interval to maintain stable performance across different hardware.
