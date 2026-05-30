# Step 7: Diagnostics & Simulation Utilities

## Objective
Create `ai_module/diagnostics.py` with reusable testing utilities that enable recognition stability validation, frame simulation (without a physical camera), performance validation, and system health checks.

## Why This Step
Testing a real-time camera-based AI system is inherently difficult:
- You can't run automated tests that require a physical webcam on CI/CD
- You can't simulate specific conditions (exact darkness, exact blur level) with a real camera
- You need deterministic test inputs to validate recognition consistency

This module solves these problems by providing synthetic frame generation and recognition validation tools.

## Tasks

### Part A: FrameSimulator

1. Create `FrameSimulator` class for generating synthetic test frames:

2. Implement frame generators (all return `np.ndarray` of shape `(height, width, 3)`):
   - `create_normal_frame(width=640, height=480)` — random noise with moderate brightness (128 ± 40)
   - `create_dark_frame(width=640, height=480)` — low brightness (mean ~20), simulates poor lighting
   - `create_bright_frame(width=640, height=480)` — high brightness (mean ~250), simulates overexposure
   - `create_blurry_frame(width=640, height=480)` — apply heavy Gaussian blur (kernel 31×31), simulates motion blur
   - `add_noise(frame, intensity=0.1)` — adds Gaussian noise to an existing frame, simulates camera sensor noise

3. All generators return BGR format (matching OpenCV convention).

### Part B: RecognitionStabilityTester

4. Create `RecognitionStabilityTester` class for validating recognition behavior:

5. Implement `test_consistency(recognizer, encoding, iterations=50) -> dict`:
   - Feeds the exact same encoding to `recognizer.identify_optimized()` N times
   - Reports: match name consistency (should be 100%), confidence mean/std, any mismatches
   - Returns: `{"consistency_pct": float, "confidence_mean": float, "confidence_std": float, "mismatches": int}`

6. Implement `test_confidence_stability(recognizer, encoding, noise_std=0.01, iterations=50) -> dict`:
   - Adds small Gaussian noise to the encoding each iteration
   - Reports: confidence mean, std deviation, min, max, and whether std is within acceptable bounds (< 5%)
   - Returns: `{"confidence_mean": float, "confidence_std": float, "confidence_min": float, "confidence_max": float, "stable": bool}`

7. Implement `test_multi_face_handling(recognizer, encodings_list, iterations=10) -> dict`:
   - Processes multiple encodings per iteration (simulates multiple faces in frame)
   - Reports: total faces processed, successes, failures, average processing time
   - Returns: `{"total_faces": int, "successes": int, "failures": int, "avg_time_ms": float}`

### Part C: PerformanceValidator

8. Create `PerformanceValidator` class:

9. Implement `validate_fps_stability(tracker, duration_ticks=1000) -> dict`:
   - Runs `tracker.tick()` N times with small delays
   - Reports: FPS mean, std, min, max, and whether variance is within 20% of target
   - Returns: `{"fps_mean": float, "fps_std": float, "fps_min": float, "fps_max": float, "stable": bool}`

10. Implement `validate_memory_stability(iterations=1000) -> dict`:
    - Tracks `tracemalloc` memory over N iterations of dummy work
    - Reports: start memory, end memory, peak memory, growth rate (bytes/iteration)
    - Returns: `{"start_bytes": int, "end_bytes": int, "peak_bytes": int, "growth_per_iteration": float, "stable": bool}`

11. Implement `generate_diagnostics_report(output_dir=None) -> str`:
    - Collects all diagnostic data into a timestamped report file
    - Saves to `reports/diagnostics_report_YYYYMMDD_HHMMSS.txt`
    - Returns the file path

### Part D: SystemHealthChecker

12. Create `SystemHealthChecker` class:

13. Implement individual check methods (each returns `(bool, str)`):
    - `check_camera(camera_id=0)` — tries to open `cv2.VideoCapture`, returns status
    - `check_encodings(encoding_file)` — checks if file exists, is valid pickle, has correct structure
    - `check_dependencies()` — verifies `cv2`, `face_recognition`, `numpy` are importable with versions
    - `check_disk_space(path, min_mb=100)` — checks available disk space at the given path

14. Implement `run_all_checks() -> dict`:
    - Runs all individual checks
    - Returns aggregated results: `{"camera": (bool, str), "encodings": (bool, str), "dependencies": (bool, str), "disk_space": (bool, str), "overall_healthy": bool}`

## Design Details

### Class Structure
```
FrameSimulator
├── create_normal_frame(width, height) → np.ndarray
├── create_dark_frame(width, height) → np.ndarray
├── create_bright_frame(width, height) → np.ndarray
├── create_blurry_frame(width, height) → np.ndarray
└── add_noise(frame, intensity) → np.ndarray

RecognitionStabilityTester
├── test_consistency(recognizer, encoding, iterations) → dict
├── test_confidence_stability(recognizer, encoding, noise_std, iterations) → dict
└── test_multi_face_handling(recognizer, encodings_list, iterations) → dict

PerformanceValidator
├── validate_fps_stability(tracker, duration_ticks) → dict
├── validate_memory_stability(iterations) → dict
└── generate_diagnostics_report(output_dir) → str

SystemHealthChecker
├── check_camera(camera_id) → (bool, str)
├── check_encodings(encoding_file) → (bool, str)
├── check_dependencies() → (bool, str)
├── check_disk_space(path, min_mb) → (bool, str)
└── run_all_checks() → dict
```

## Dependencies
- Step 1 (config values for thresholds and paths)
- Step 2 (ErrorTracker for health context)
- OpenCV, NumPy, face_recognition (existing dependencies)

## Files Created
- `ai_module/diagnostics.py`

## Expected Outcome
A comprehensive diagnostics module that enables automated testing of recognition stability, frame quality handling, and system health — all without requiring a physical webcam. Test suites in Steps 8–10 will import and use these utilities extensively.
