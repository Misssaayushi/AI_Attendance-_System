# Step 5: Activity Monitor

## Objective
Create `ai_module/activity_monitor.py` with an event-driven activity logging system that records all recognition events, unknown detections, cooldown blocks, and security flags to both an in-memory buffer and a persistent JSONL file.

## Why This Step
The current system has no historical record of what happened during a recognition session. After the demo ends, there's no data to review. An activity monitor provides a timeline of all events — who was recognized, when unknowns appeared, how many cooldown blocks occurred — essential for post-session analysis and professional reporting.

## Tasks

### Part A: ActivityEvent Dataclass

1. Create `ActivityEvent` dataclass:
   - `event_type: str` — one of: "recognition", "unknown", "cooldown", "security", "system"
   - `timestamp: float` — `time.time()` of the event
   - `student_id: Optional[str]` — student involved (None for system events)
   - `details: dict` — event-specific data (confidence, status, alert_id, etc.)

### Part B: SessionStats Dataclass

2. Create `SessionStats` dataclass:
   - `session_start: float` — timestamp when session began
   - `total_recognitions: int` — total face recognition attempts
   - `successful_recognitions: int` — recognitions that identified a known person
   - `unique_students: set` — set of unique student IDs verified
   - `unknown_detections: int` — total unknown face detections
   - `cooldown_blocks: int` — total cooldown-blocked attempts
   - `security_flags: int` — total security events logged
   - `avg_confidence: float` — running average confidence score
   - `peak_confidence: float` — highest confidence seen
   - `total_frames_processed: int` — frames that went through recognition
   - `alerts_triggered: int` — unknown person alerts triggered

### Part C: ActivityMonitor Class

3. Create `ActivityMonitor` class:

   **Constructor** `__init__()`:
   - Initialize `SessionStats` with current timestamp
   - Initialize in-memory event buffer (list with max size from config)
   - Open JSONL file handle in append mode
   - Initialize write buffer counter for batched flushing
   - Get logger instance

   **Logging methods**:

4. `log_recognition(student_id, name, confidence, verified)`:
   - Creates `ActivityEvent` with type "recognition"
   - Updates `SessionStats`: increment total_recognitions, update avg_confidence, update peak_confidence
   - If verified: add student_id to unique_students set, increment successful_recognitions
   - Appends to buffer and conditionally flushes

5. `log_unknown_detection(alert_event=None)`:
   - Creates `ActivityEvent` with type "unknown"
   - Updates `SessionStats`: increment unknown_detections
   - If `alert_event` is provided: increment alerts_triggered, include alert_id in details
   - Appends to buffer

6. `log_cooldown_event(student_id, remaining_seconds)`:
   - Creates `ActivityEvent` with type "cooldown"
   - Updates `SessionStats`: increment cooldown_blocks
   - Details include remaining_seconds for analytics
   - Appends to buffer

7. `log_security_event(event_type, details)`:
   - Creates `ActivityEvent` with type "security"
   - Updates `SessionStats`: increment security_flags
   - Appends to buffer

   **Query methods**:

8. `get_session_stats() → SessionStats`:
   - Returns a copy of the current session statistics
   - Thread-safe read (uses simple attribute access — SessionStats fields are primitives)

9. `get_recent_activity(count=20) → list[ActivityEvent]`:
   - Returns the last N events from the in-memory buffer
   - Used for live activity display if needed

   **Persistence methods**:

10. `_append_to_buffer(event: ActivityEvent)`:
    - Adds event to in-memory list
    - If buffer size exceeds `ACTIVITY_LOG_MAX_ENTRIES`: evict oldest 10% of entries
    - Increment write counter; if counter reaches `ACTIVITY_LOG_FLUSH_INTERVAL`: call `flush()`

11. `flush()`:
    - Writes all un-flushed events to JSONL file as one JSON object per line
    - Uses `json.dumps()` with event converted to dict
    - Resets write counter
    - Handles file I/O errors gracefully (log warning, don't crash)

12. `cleanup()`:
    - Calls `flush()` for any remaining buffered events
    - Closes file handle
    - Logs final session stats summary

## Design Details

### JSONL File Format
Each line in `activity_log.jsonl` is a valid JSON object:
```json
{"event_type": "recognition", "timestamp": 1717225200.123, "student_id": "101_John", "details": {"name": "101_John", "confidence": 92.4, "verified": true}}
{"event_type": "unknown", "timestamp": 1717225205.456, "student_id": null, "details": {"alert_triggered": true, "alert_id": "a1b2c3d4"}}
{"event_type": "cooldown", "timestamp": 1717225210.789, "student_id": "101_John", "details": {"remaining_seconds": 1470.5}}
```

### Memory Management
- In-memory buffer is capped at `ACTIVITY_LOG_MAX_ENTRIES` (default: 10,000)
- When cap is reached, oldest 10% (1,000 entries) are evicted
- Evicted entries are already persisted to disk (flushed in batches of 10)
- Total memory overhead: ~50 KB for 10,000 lightweight event objects

### File I/O Strategy
- File is opened once in `__init__` and kept open for append
- Writes are batched: every `ACTIVITY_LOG_FLUSH_INTERVAL` events (default: 10)
- Each `flush()` writes multiple lines at once, reducing system call overhead
- File handle is closed in `cleanup()` which is called from `finally` block

### Thread Safety
- `ActivityMonitor` is NOT thread-safe by design — it's called only from the main recognition loop
- If future phases need thread safety, a lock can be added around buffer operations

## Dependencies
- Step 1 (config values: `ACTIVITY_LOG_*`)

## Files Created
- `ai_module/activity_monitor.py`

## Expected Outcome
A lightweight activity monitoring system that records every significant event during a recognition session. Events are buffered in memory for fast access and periodically flushed to a JSONL file for persistence. Session statistics are maintained in real-time and can be queried at any point for HUD display or report generation.
