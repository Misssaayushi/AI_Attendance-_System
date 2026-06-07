# Step 4: Frame Optimizer

## Objective
Create a `FrameOptimizer` class in `ai_module/optimization.py` that implements the crop-then-encode strategy and memory-efficient frame preprocessing.

## Why This Step
The single most expensive operation in the pipeline is `face_recognition.face_encodings()`. Currently, this is called on the full 640×480 frame (~307K pixels). By cropping the face region with padding first, we reduce the input to ~36K pixels — an ~8.5× reduction in compute for the dlib encoding model.

## Tasks

1. Add `FrameOptimizer` class to `optimization.py`.

2. Implement RGB conversion with reuse:
   - `prepare_frame(frame)` — converts a BGR frame to RGB once.
   - Store the RGB frame so it can be reused for both detection and encoding within the same processing interval.
   - Avoids calling `cv2.cvtColor()` multiple times per frame.

3. Implement crop-then-encode:
   - `crop_face_region(rgb_frame, face_location, padding)` — extracts the face region with configurable padding around the bounding box.
   - Clamp coordinates to frame boundaries to avoid out-of-bounds errors.
   - Returns the cropped RGB region ready for `face_recognition.face_encodings()`.

4. Implement optimized encoding generation:
   - `generate_encoding(rgb_frame, face_location)` — crops the face region, then calls `face_recognition.face_encodings()` on the smaller crop.
   - Falls back to full-frame encoding if the crop fails or produces no encoding.
   - Returns `(encoding, success)` tuple.

5. Implement batch face processing:
   - `process_faces(rgb_frame, face_locations)` — processes multiple faces efficiently.
   - For each face location, crops and encodes individually.
   - Returns list of `(encoding, face_location)` tuples.

6. Handle edge cases:
   - Face location extends beyond frame boundaries → clamp to frame edges.
   - Cropped region too small for encoding → fall back to full frame.
   - No encoding returned for a crop → log warning, skip that face.

## Crop-Then-Encode Detail

```
Current (full frame encoding):
  640×480 frame → face_encodings(frame, [location]) → ~50-120ms

Optimized (cropped region encoding):
  640×480 frame → crop 190×190 region → face_encodings(crop) → ~15-30ms
```

Padding of 30px around the face bounding box provides sufficient context for the dlib model to generate accurate encodings while keeping the region small.

## Design Details

```
FrameOptimizer
├── _padding: int (from FACE_CROP_PADDING)
├── prepare_frame(bgr_frame) → np.ndarray (RGB)
├── crop_face_region(rgb_frame, face_location, padding) → np.ndarray
├── generate_encoding(rgb_frame, face_location) → tuple[np.ndarray | None, bool]
└── process_faces(rgb_frame, face_locations) → list[tuple]
```

## Dependencies
- Step 1 (config value: `FACE_CROP_PADDING`)
- Step 2 (encoding cache for comparison data)

## Files Modified
- `ai_module/optimization.py` (add `FrameOptimizer` class)

## Expected Outcome
Face encoding generation becomes 3–5× faster by operating on a small cropped region instead of the full frame, while maintaining recognition accuracy.
