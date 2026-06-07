# Step 3: Registration Script (register_face.py)

## Objective
Build the main registration pipeline that ties together the webcam, detector, validator, and file storage into a smooth, user-friendly capture experience.

## Tasks
- Accept student ID and name via terminal input.
- Create the student's dataset folder (`dataset/{id}_{name}/`).
- Open webcam and run live detection with the Phase 2 `FaceDetector`.
- On each valid frame (passes `FaceValidator`), save the image and increment the counter.
- Display live overlays: capture progress, quality status, guidance messages.
- Handle edge cases: duplicate IDs, no face, multiple faces, timeout.
- Cleanup webcam on completion or error.

## User Experience Flow
1. Terminal asks: "Enter Student ID:" → "Enter Student Name:"
2. Webcam opens with a guide box and status messages.
3. System auto-captures valid frames every 0.5 seconds.
4. Progress overlay: "Capturing Sample 7/20"
5. On completion: "Registration Complete! 20 samples saved."

## Expected Outcome
A standalone script that any student can run to register their face.
