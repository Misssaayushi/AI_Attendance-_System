# Step 4: Real-Time Recognition Script (recognize_faces.py)

## Objective
Create the main application entry point for Phase 4 that displays the live camera feed with recognition overlays.

## Tasks
- Initialize `CameraHandler`, `FaceDetector`, and `FaceRecognizer`.
- Loop through camera frames.
- Run recognition logic every `N` frames for performance.
- Use `FrameUtils` to draw boxes and labels:
    - Green Box: Recognized Student.
    - Red/Yellow Box: Unknown Person.
- Display a professional UI with student names and live stats.

## Expected Outcome
A fully functional real-time attendance system (Recognition mode) that can be demonstrated.
