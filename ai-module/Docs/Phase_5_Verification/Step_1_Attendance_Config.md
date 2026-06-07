# Step 1: Attendance Configuration

## Objective
Extend `config.py` with the parameters needed for smart attendance verification.

## Tasks
- Add `ATTENDANCE_COOLDOWN_MINUTES`: Time to wait before re-marking a student (Default: 30).
- Add `MIN_CONFIDENCE_THRESHOLD`: Minimum AI confidence to log attendance (Default: 80%).
- Add `STABILITY_FRAMES`: Number of consecutive frames needed for verification (Default: 3).

## Expected Outcome
A set of rules that prevents the system from being "too sensitive" or spamming duplicate data.
