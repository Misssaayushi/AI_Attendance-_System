# Step 3: Recognition Engine (FaceRecognizer)

## Objective
Develop the core `FaceRecognizer` class in `utils.py` that handles the heavy lifting of comparing live faces against the database.

## Tasks
- Create `FaceRecognizer` class that uses `EncodingManager`.
- Implement `identify_face(frame, face_location)`:
    - Generates 128D encoding for the detected face.
    - Uses `face_recognition.compare_faces` to find matches.
    - Uses `face_recognition.face_distance` to find the most accurate match.
- Return the student name and a confidence score.

## Expected Outcome
A modular "Brain" for the system that can identify any face passed to it.
