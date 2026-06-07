# Step 2: Error Handler Module

## Objective
Create `ai_module/error_handler.py` with centralized error classification, tracking, and health monitoring — providing the foundation for all error handling across the recognition pipeline.

## Why This Step
Currently, all errors go through a single `logger.error()` call with no severity classification, rate tracking, or health assessment. The system has no way to answer: "Is the AI pipeline healthy right now?" or "How many errors have occurred in the last minute?" This step creates the infrastructure to answer those questions.

## Tasks

1. Create `ai_module/error_handler.py` with the following components.

2. Implement `ErrorCategory` enum:
   - `TRANSIENT` — retryable errors that resolve on their own (e.g., single frame read failure, temporary encoding generation timeout)
   - `RECOVERABLE` — errors that need a recovery action (e.g., webcam disconnect, corrupted encoding file)
   - `FATAL` — errors where the system cannot continue (e.g., no camera device exists, missing Python dependency)

3. Implement `SystemError` dataclass:
   - `category: ErrorCategory` — severity classification
   - `source: str` — which component raised it (e.g., "CameraHandler", "FaceDetector", "EncodingCache")
   - `message: str` — human-readable error description
   - `timestamp: float` — `time.time()` when error occurred
   - `exception: Optional[Exception]` — the original exception object, if any

4. Implement `ErrorTracker` class:
   - Maintains a rolling deque of `SystemError` objects
   - `record_error(error: SystemError)` — logs the error and appends to the deque
   - `get_error_rate(source: str) -> float` — returns errors per minute for a specific source within the configured window
   - `get_total_error_rate() -> float` — returns aggregate errors per minute across all sources
   - `is_healthy() -> bool` — returns `True` if total error rate is below `ERROR_RATE_THRESHOLD`
   - `get_health_summary() -> dict` — returns a snapshot with total errors, per-source breakdown, error rate, and health status
   - `clear()` — resets all tracked errors (useful for testing)

5. Thread safety:
   - All `ErrorTracker` methods must be thread-safe using `threading.Lock()`
   - The `APIDispatcher` runs in background threads and may call `record_error()` concurrently

## Design Details

```
ErrorCategory (Enum)
├── TRANSIENT
├── RECOVERABLE
└── FATAL

SystemError (dataclass)
├── category: ErrorCategory
├── source: str
├── message: str
├── timestamp: float
└── exception: Optional[Exception]

ErrorTracker
├── _errors: deque[SystemError]
├── _lock: threading.Lock
├── record_error(error) → None
├── get_error_rate(source) → float
├── get_total_error_rate() → float
├── is_healthy() → bool
├── get_health_summary() → dict
└── clear() → None
```

## Error Flow Architecture

```
Any Component (CameraHandler, FaceDetector, etc.)
    │
    ├── catches exception
    ├── creates SystemError(category, source, message)
    ├── calls error_tracker.record_error(error)
    │
    └── ErrorTracker
        ├── logs with appropriate severity
        ├── appends to rolling deque
        ├── prunes expired entries (older than ERROR_RATE_WINDOW_SECONDS)
        └── updates health status
```

## Dependencies
- Step 1 (config values: `ERROR_RATE_WINDOW_SECONDS`, `ERROR_RATE_THRESHOLD`)

## Files Created
- `ai_module/error_handler.py` (initial creation with `ErrorCategory`, `SystemError`, `ErrorTracker`)

## Expected Outcome
A centralized error tracking system that classifies errors by severity, calculates error rates over a sliding window, and provides a simple `is_healthy()` API for the recognition loop to check system status.
