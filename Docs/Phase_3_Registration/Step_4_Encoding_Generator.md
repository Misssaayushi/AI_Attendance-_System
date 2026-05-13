# Step 4: Encoding Generator (encode_faces.py)

## Objective
Build a batch encoding script that processes all saved images in the `dataset/` folder and generates 128-dimensional face encoding vectors stored as `.pkl` files.

## Tasks
- Scan `dataset/` for all student folders.
- For each student folder, load all `.jpg` images.
- For each image: detect face → generate encoding using `face_recognition.face_encodings()`.
- Save individual encoding file: `encodings/{id}_{name}.pkl`.
- Build a consolidated `all_encodings.pkl` containing every student's data for fast bulk-loading.
- Log success/failure counts per student.

## Why Separate from Registration?
Decoupling capture from encoding allows us to:
- Re-encode all students if we upgrade the AI model.
- Fix a bad image and re-run without re-capturing.
- Run encoding as a background batch job.

## Expected Outcome
Running this script produces ready-to-use encoding files for Phase 4 (Recognition).
