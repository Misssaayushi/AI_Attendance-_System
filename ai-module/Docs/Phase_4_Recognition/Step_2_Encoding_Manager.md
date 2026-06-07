# Step 2: In-Memory Encoding Manager

## Objective
Implement an `EncodingManager` in `utils.py` that loads registered student data into RAM once, preventing expensive disk I/O during real-time processing.

## Tasks
- Create `EncodingManager` class.
- Implement `load_known_faces()`: Reads the consolidated `.pickle` file.
- Store data in a dictionary or parallel lists for O(1) or O(N) access.
- Add error handling for missing or corrupt files.

## Expected Outcome
A lightning-fast way for the AI to access registered students without slowing down the camera feed.
