# Step 2: Attendance Manager (AttendanceManager)

## Objective
Implement an `AttendanceManager` class in `utils.py` to handle the logic of who has been marked and when.

## Tasks
- Create `AttendanceManager` class.
- Implement `can_verify(student_id)`: Checks the in-memory cooldown dictionary.
- Implement `mark_verified(student_id)`: Updates the last seen timestamp.
- Add logic to track "Stability Streaks" (consecutive frames).

## Expected Outcome
A module that makes the final decision on whether to "Ding" the attendance bell.
