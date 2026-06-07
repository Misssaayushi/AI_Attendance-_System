# Step 5: Async API Dispatcher

## Objective
Create an `APIDispatcher` class in `ai_module/optimization.py` that wraps attendance API calls in a background thread to prevent blocking the webcam render loop.

## Why This Step
Currently, `api_service.send_verified_attendance()` is called synchronously inside the recognition loop. When the backend is slow or unreachable, this blocks frame rendering for up to 2 seconds (the `API_TIMEOUT_SECONDS` value). The dispatcher offloads these calls to a background thread so the webcam feed continues smoothly.

## Tasks

1. Add `APIDispatcher` class to `optimization.py`.

2. Implement non-blocking dispatch:
   - `dispatch(api_service, student_id, name, confidence)` — spawns a `threading.Thread` to call `api_service.send_verified_attendance()`.
   - The main recognition loop continues immediately after dispatch.
   - Thread is set as daemon so it won't block program exit.

3. Implement result retrieval:
   - `get_result(student_id)` — checks if a dispatched call has completed.
   - Returns `(completed: bool, response: AttendanceAPIResponse | None)`.
   - Uses a thread-safe `dict` protected by `threading.Lock()`.

4. Implement result caching:
   - Store completed results in a dict keyed by `student_id`.
   - Results are kept for `API_FEEDBACK_DISPLAY_SECONDS` (from config).
   - `collect_expired()` removes results older than the display window.

5. Implement concurrency safety:
   - Prevent duplicate dispatches for the same `student_id` while one is in-flight.
   - `is_pending(student_id)` — returns True if a call is currently in progress.
   - Track pending dispatches via a `set()` protected by lock.

6. Implement cleanup:
   - `cleanup()` — called on system shutdown, waits for pending threads (with timeout).
   - Automatic expired result cleanup every `API_FEEDBACK_CLEANUP_INTERVAL` frames.

7. Maintain backward compatibility:
   - When `API_DISPATCH_ASYNC` is False, `dispatch()` falls back to synchronous execution.
   - This allows easy toggling for debugging.

## Thread Safety Design

```
Main Thread (recognition loop)          Background Thread (API call)
    │                                       │
    ├── dispatch(student_id) ──────────────►│ send_verified_attendance()
    │   (returns immediately)               │ ...waiting for HTTP...
    ├── render frame                        │
    ├── render frame                        │
    ├── get_result(student_id)              │
    │   → (False, None)                     │
    ├── render frame                        │
    │                                       ├── response received
    │                                       ├── store in results dict (locked)
    ├── get_result(student_id)              │
    │   → (True, AttendanceAPIResponse)     │
    └── display feedback                    └── thread exits
```

## Design Details

```
APIDispatcher
├── _results: dict[str, tuple[AttendanceAPIResponse, float]]
├── _pending: set[str]
├── _lock: threading.Lock
├── dispatch(api_service, student_id, name, confidence) → None
├── get_result(student_id) → tuple[bool, AttendanceAPIResponse | None]
├── is_pending(student_id) → bool
├── collect_expired(max_age_seconds) → int
└── cleanup(timeout) → None
```

## Dependencies
- Step 1 (config values: `API_DISPATCH_ASYNC`, `API_FEEDBACK_DISPLAY_SECONDS`, `API_FEEDBACK_CLEANUP_INTERVAL`)
- Phase 6 `api_service.py` (unchanged — dispatcher wraps it, doesn't modify it)

## Files Modified
- `ai_module/optimization.py` (add `APIDispatcher` class)

## Expected Outcome
API calls never block the frame loop. The webcam feed maintains smooth FPS even when the backend is slow, unreachable, or timing out.
