# Step 8: Benchmarking Utilities

## Objective
Create a `PerformanceBenchmark` class in `ai_module/optimization.py` that measures and reports encoding load speed, per-frame processing time, recognition latency, and memory usage.

## Why This Step
Without concrete metrics, optimization is guesswork. The benchmarking utility provides before/after comparisons, identifies remaining bottlenecks, and generates reports that can be shared with stakeholders to demonstrate Phase 7 improvements.

## Tasks

1. Add `PerformanceBenchmark` class to `optimization.py`.

2. Implement encoding load benchmark:
   - `benchmark_encoding_load(path, iterations=5)` — measures time to load the encoding file N times, reports min/max/avg/median load time.
   - Reports encoding count, file size, and memory estimate.

3. Implement per-frame timing:
   - `start_frame()` / `end_frame()` — bracket a frame processing cycle.
   - Track cumulative stats: total frames, total processing time, min/max/avg frame time.
   - Separate timing for detection vs. encoding vs. comparison phases.

4. Implement recognition latency measurement:
   - `benchmark_recognition(frame, face_locations, recognizer, iterations=10)` — measures identification time for a set of face locations.
   - Reports per-face latency.

5. Implement memory usage tracking:
   - Use `sys.getsizeof()` for encoding arrays.
   - Use `tracemalloc` (if available) for overall memory snapshots.
   - Report: encoding matrix memory, total Python heap, peak memory.

6. Implement report generation:
   - `generate_report(output_dir)` — writes a timestamped report file to `reports/`.
   - Report format: plain text with sections for each metric category.
   - Include system info: Python version, platform, CPU count.

7. Implement summary statistics:
   - `get_summary()` — returns a dict of all collected metrics.
   - `print_summary()` — prints a formatted summary to console.

## Report Format

```
=== AI Attendance System - Performance Benchmark Report ===
Date: 2026-05-29 22:30:00
Python: 3.11.5 | Platform: macOS-14.0 | CPUs: 8

--- Encoding Load ---
File: encodings.pickle (12.8 KB)
Encodings: 20 faces
Load Time: avg=1.2ms, min=0.8ms, max=2.1ms
Memory: 10.2 KB (NumPy matrix)

--- Frame Processing ---
Frames Processed: 500
Avg Frame Time: 42.3ms (23.6 FPS)
Detection: avg=18.2ms
Encoding: avg=15.1ms (crop-then-encode)
Comparison: avg=0.3ms

--- Recognition Latency ---
Per-Face Recognition: avg=15.4ms
Best: 12.1ms | Worst: 22.8ms

--- Memory ---
Encoding Matrix: 10.2 KB
Peak Heap: 45.2 MB
```

## Dependencies
- Step 1 (config value: `BENCHMARK_REPORT_DIR`)
- Step 2 (EncodingCache for load benchmarks)
- Step 3 (PerformanceTracker for frame-time data)

## Files Modified
- `ai_module/optimization.py` (add `PerformanceBenchmark` class)

## Expected Outcome
A reusable benchmarking utility that can generate performance reports on demand, providing concrete metrics for validating Phase 7 optimizations.
