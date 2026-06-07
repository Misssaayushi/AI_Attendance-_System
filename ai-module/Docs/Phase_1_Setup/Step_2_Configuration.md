# Step 2: Centralized Configuration

## Objective
Create a single source of truth for all AI system settings to avoid hardcoding paths and parameters across multiple files.

## Tasks
- Create `ai_module/config.py`.
- Define path constants using `os` or `pathlib`.
- Configure camera settings (Camera ID, resolution).
- Define recognition thresholds (e.g., Confidence > 0.8).

## Expected Outcome
A `config.py` file that allows the entire AI module to be reconfigured from one place.
