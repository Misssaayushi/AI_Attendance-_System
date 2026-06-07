# Step 1: Detection Config & Utility Expansion

## Objective
Update the configuration and utility files to support facial coordinate scaling and professional box rendering.

## Tasks
- Add `FACE_DETECTION_MODEL` ("hog") to `config.py`.
- Add `FRAME_RESIZE_SCALE` (0.25) to `config.py`.
- Add `draw_face_box` helper to `utils.py`.
- Add `scale_face_locations` helper to `utils.py`.

## Expected Outcome
Utilities ready to handle real-time detection data.
