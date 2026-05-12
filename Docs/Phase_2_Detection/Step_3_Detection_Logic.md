# Step 3: Detection Logic Integration

## Objective
Update the webcam stream logic to incorporate the new face detection pipeline in real-time.

## Tasks
- Modify the main loop in the test/demo scripts.
- Call `FaceDetector.detect_faces()`.
- Scale coordinates back to original resolution.

## Expected Outcome
Live webcam feed showing bounding boxes around detected faces.
