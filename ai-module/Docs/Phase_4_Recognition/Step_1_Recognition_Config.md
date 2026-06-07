# Step 1: Recognition Configuration

## Objective
Update `config.py` with the settings required to tune the recognition engine's accuracy and performance.

## Tasks
- Ensure `RECOGNITION_TOLERANCE` is set (Default: 0.6).
- Add `RECOGNITION_PROCESS_INTERVAL` (e.g., 2) — Process every 2nd frame to save CPU.
- Add `UNKNOWN_LABEL` (Default: "Unknown Person") — String to display when no match is found.

## Expected Outcome
A central location to adjust how "strict" the AI is and how fast it runs.
