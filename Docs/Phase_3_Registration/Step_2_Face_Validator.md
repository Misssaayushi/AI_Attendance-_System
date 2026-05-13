# Step 2: Face Quality Validator

## Objective
Create a `FaceValidator` class in `utils.py` that acts as a quality gate — every captured frame must pass blur, brightness, and size checks before being saved.

## Tasks
- Implement `check_blur(frame)` — uses OpenCV Laplacian to measure sharpness.
- Implement `check_brightness(frame)` — calculates mean pixel intensity.
- Implement `check_face_size(face_location)` — verifies bounding box is large enough.
- Implement `validate_frame(frame, face_locations)` — runs all checks, returns pass/fail with a reason string.

## Why This Matters
Bad-quality images produce bad encodings, which cause false recognitions. This step prevents garbage data from entering the system.

## Expected Outcome
A reusable validator that can be plugged into any future capture workflow.
