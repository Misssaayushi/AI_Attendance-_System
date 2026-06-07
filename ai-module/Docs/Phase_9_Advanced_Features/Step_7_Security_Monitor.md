# Step 7: Security Monitor

## Objective
Add a `SecurityMonitor` class to `ai_module/error_handler.py` that detects suspicious recognition patterns: repeated unknown presence, confidence instability, and rapid identity switching. Security events are logged to a dedicated audit trail.

## Why This Step
A professional attendance system should detect potential tampering or anomalous behavior. While this isn't a full security system, detecting patterns like someone repeatedly appearing as unknown (possible intruder) or confidence scores oscillating wildly (possible photo/video spoofing attempt) adds a meaningful security layer suitable for a university demo.

## Tasks

### Part A: SecurityMonitor Class

1. Create `SecurityMonitor` class in `error_handler.py`:

   **Constructor** `__init__()`:
   - Initialize rolling unknown counter (int)
   - Initialize low-confidence streak tracker (dict: student_id → consecutive count)
   - Initialize identity history tracker (dict: face_position_key → list of recent names)
   - Initialize security flag counter
   - Initialize suspicious state flag (bool)
   - Open security alert log file handle (`SECURITY_ALERT_LOG_FILE`)
   - Get logger instance

### Part B: Unknown Detection Tracking

2. `track_unknown_detection()`:
   - Increment rolling unknown counter
   - If counter >= `SECURITY_REPEATED_UNKNOWN_THRESHOLD`:
     - Set `suspicious` flag to True
     - Log security event: "Repeated unknown detections exceeded threshold"
     - Write to security alert log file
     - Increment security flag counter

3. `reset_unknown_counter()`:
   - Called when a known person is detected
   - Resets rolling unknown counter to 0
   - Does NOT clear suspicious flag (once flagged, stays flagged for the session)

### Part C: Confidence Instability Detection

4. `track_low_confidence(student_id, confidence)`:
   - If confidence < `MIN_CONFIDENCE_THRESHOLD` (from existing config):
     - Increment consecutive low-confidence count for this student
     - If count >= `SECURITY_LOW_CONFIDENCE_STREAK_THRESHOLD`:
       - Log security event: "Unstable confidence for {student_id}"
       - Set suspicious flag
       - Reset streak counter for this student
   - If confidence >= threshold:
     - Reset streak counter for this student to 0

### Part D: Rapid Identity Switching Detection

5. `track_identity(face_position_key, name)`:
   - `face_position_key` is a rough location hash (e.g., `f"{center_x//50}_{center_y//50}"`) to group detections from the same physical face position
   - Maintains a sliding window of last 3 names seen at this position
   - If 3 different names appear in the last 3 frames at the same position:
     - Log security event: "Rapid identity switching detected"
     - Set suspicious flag
     - Increment security flag counter

### Part E: Query Methods

6. `is_suspicious() → bool`:
   - Returns True if any security threshold has been breached during the session

7. `get_security_summary() → dict`:
   - Returns:
     - `suspicious` — current suspicious state
     - `unknown_counter` — current rolling unknown count
     - `security_flags` — total flags triggered
     - `low_confidence_students` — list of student IDs with recent instability
     - `identity_switch_events` — count of identity switching detections

8. `track_recognition_attempt(student_id, confidence, verified, face_location=None)`:
   - Master tracking method that calls the appropriate sub-trackers:
     - If student_id is Unknown → `track_unknown_detection()`
     - Else → `reset_unknown_counter()`, `track_low_confidence(student_id, confidence)`
   - If `face_location` provided → `track_identity(position_key, student_id)`

### Part F: Cleanup

9. `cleanup()`:
   - Closes security alert log file handle

## Design Details

### Face Position Hashing
To detect identity switching, we need to correlate detections from the same physical face across frames:
```python
def _get_position_key(self, face_location):
    top, right, bottom, left = face_location
    center_x = (left + right) // 2
    center_y = (top + bottom) // 2
    # Quantize to 50px grid to tolerate slight movement
    return f"{center_x // 50}_{center_y // 50}"
```

### Security Alert Log Format
Separate from the main `ai_system.log`, the security log uses a structured format:
```
2026-06-01 09:45:12 | SECURITY | REPEATED_UNKNOWN | count=12 | threshold=10
2026-06-01 09:47:30 | SECURITY | LOW_CONFIDENCE_STREAK | student=101_John | streak=5
2026-06-01 09:48:15 | SECURITY | IDENTITY_SWITCH | position=6_4 | names=John,Jane,Unknown
```

### Memory Management
- Identity history uses a `deque(maxlen=3)` per position key → bounded memory
- Position keys are cleaned periodically (every 100 frames) to remove stale entries
- Low-confidence tracker stores at most one counter per student → bounded by database size

### Integration Point
- `SecurityMonitor` is called from the main recognition loop (Step 9)
- It does NOT modify recognition behavior — it only observes and flags
- The suspicious state is displayed in the system HUD as an amber/red indicator

## Dependencies
- Step 1 (config values: `SECURITY_*`)
- Existing `MIN_CONFIDENCE_THRESHOLD` from config (already present)

## Files Modified
- `ai_module/error_handler.py` (add `SecurityMonitor` class)

## Expected Outcome
The system now monitors for suspicious patterns during recognition sessions. Repeated unknown presences, confidence instability, and identity switching are detected and logged to a dedicated security audit trail. The suspicious state can be displayed in the overlay HUD and is included in session reports. No existing error handling behavior is modified.
