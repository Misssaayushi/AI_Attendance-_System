# Step 4: Cooldown Enhancement

## Objective
Enhance the existing `AttendanceManager` class in `ai_module/utils.py` with configurable cooldown profiles, remaining time calculation, a recognition lock registry, and duplicate event counting — without breaking backward compatibility.

## Why This Step
The current cooldown system works but provides minimal user feedback. A student on cooldown only sees "Already Verified (Cooldown)" with no indication of how long they need to wait. Adding remaining time display, named profiles for different scenarios (lecture vs. exam), and a lock registry improves both UX and demo professionalism.

## Tasks

### Part A: Configurable Cooldown Profiles

1. Add `set_cooldown_profile(profile_name)` method:
   - Accepts profile name from `COOLDOWN_CONFIGURABLE_PROFILES` dict
   - Updates `self.cooldown_minutes` to the profile's duration
   - Logs the profile change
   - Raises `ValueError` if profile name is not found

2. Add `get_active_profile() → str` method:
   - Returns the name of the currently active cooldown profile
   - Default: `ACTIVE_COOLDOWN_PROFILE` from config

3. Store active profile name as `self._active_profile` instance variable

### Part B: Remaining Cooldown Calculation

4. Add `get_cooldown_remaining(student_id) → Optional[float]` method:
   - If student is not in cooldown → return None
   - If student is in cooldown → return remaining seconds as float
   - Calculation: `(cooldown_minutes * 60) - elapsed_seconds`
   - Returns 0.0 if cooldown just expired (edge case safety)

5. Add `format_cooldown_remaining(student_id) → Optional[str]` method:
   - Calls `get_cooldown_remaining()` and formats as "MM:SS"
   - Returns None if not in cooldown
   - Example output: "24:30" or "01:15"

### Part C: Recognition Lock Registry

6. Add `_lock_registry: dict` instance variable:
   - Maps `student_id → lock_expiry_timestamp`
   - A locked student cannot trigger even a re-scan attempt

7. Add `lock_student(student_id, duration_seconds)` method:
   - Adds student to lock registry with expiry
   - Called automatically after successful verification

8. Add `is_locked(student_id) → bool` method:
   - Returns True if student is in lock registry and lock hasn't expired
   - Cleans up expired locks lazily (on check)

### Part D: Duplicate Event Counter

9. Add `_duplicate_attempts: int` instance variable:
   - Incremented every time `verify_attendance()` returns a cooldown-blocked result

10. Add `duplicate_attempts` property:
    - Returns the current duplicate attempt count

11. Add `get_cooldown_stats() → dict` method:
    - Returns dictionary with:
      - `active_profile` — current profile name
      - `cooldown_minutes` — current duration
      - `verified_count` — total verified students
      - `duplicate_attempts` — cooldown-blocked attempts
      - `locked_count` — currently locked students

### Part E: Enhanced verify_attendance() Return

12. Modify the cooldown branch in `verify_attendance()`:
    - Current: `return False, "Already Verified (Cooldown)"`
    - Enhanced: `return False, "Already Verified (Cooldown: {remaining} remaining)"`
    - The remaining time string is appended only when `COOLDOWN_DISPLAY_REMAINING` is True
    - Increment `_duplicate_attempts` counter

## Design Details

### Backward Compatibility
- The `verify_attendance()` method signature **does not change**: still returns `(bool, str)`
- Existing callers see the same behavior — only the status string content changes slightly
- New methods (`set_cooldown_profile`, `get_cooldown_remaining`, etc.) are purely additive
- Default profile is "lecture" (30 min), matching the current `ATTENDANCE_COOLDOWN_MINUTES = 30`

### Constructor Changes
```python
def __init__(self, cooldown_minutes=ATTENDANCE_COOLDOWN_MINUTES, ...):
    # Existing code preserved...
    
    # Phase 9 additions:
    self._active_profile = ACTIVE_COOLDOWN_PROFILE
    self._lock_registry = {}
    self._duplicate_attempts = 0
```

### Lock Registry Cleanup
- Expired locks are cleaned lazily in `is_locked()` — no background thread needed
- Periodic bulk cleanup can be called from the main loop if desired

## Dependencies
- Step 1 (config values: `COOLDOWN_*`, `ACTIVE_COOLDOWN_PROFILE`)

## Files Modified
- `ai_module/utils.py` (enhance `AttendanceManager` class)

## Expected Outcome
The `AttendanceManager` class gains professional cooldown management features while remaining fully backward-compatible. Students see how long they need to wait, the system tracks duplicate attempts for analytics, and different cooldown profiles can be switched for different class scenarios (lecture, lab, exam). No existing caller breaks.
