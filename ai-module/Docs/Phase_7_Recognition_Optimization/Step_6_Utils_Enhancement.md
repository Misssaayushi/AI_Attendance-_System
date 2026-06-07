# Step 6: Utils Enhancement

## Objective
Update existing utility classes in `utils.py` and update `encode_faces.py` and `register_face.py` to use the new `EncodingCache` system, fix known issues, and prepare the utilities for the optimized recognition pipeline.

## Why This Step
The existing `FaceDetector` and `FaceRecognizer` classes work correctly but have small inefficiencies. The `EncodingManager` should delegate to the new `EncodingCache` singleton. These changes prepare the utility layer so that the recognition pipeline rewrite (Step 7) can integrate cleanly.

## Tasks

### 6.1 — Fix FaceDetector Scale-Back Calculation

**Problem:** Line 112 in `utils.py` uses `int(1 / self.scale)` which truncates to integer. With `scale=0.25`, this gives `int(4.0) = 4` (correct). But with values like `scale=0.3`, `int(3.33) = 3` causes bounding box misalignment.

**Fix:** Use float division `1.0 / self.scale` and round coordinates:
```python
inv_scale = 1.0 / self.scale
scaled_locations.append((
    int(top * inv_scale),
    int(right * inv_scale),
    int(bottom * inv_scale),
    int(left * inv_scale)
))
```

### 6.2 — Update FaceDetector to Return RGB Frame

**Current:** `detect_faces()` creates `rgb_small_frame` internally but discards it after detection.

**Change:** Add an optional `return_rgb` parameter. When True, return `(face_locations, rgb_small_frame)` so the frame optimizer can reuse the RGB conversion.

### 6.3 — Add identify_optimized() to FaceRecognizer

**Current:** `identify()` calls `face_recognition.face_encodings(frame, [face_location])` on the full frame.

**Change:** Add `identify_optimized(live_encoding)` that accepts a pre-computed encoding (from the `FrameOptimizer`) and only does the comparison step:
```python
def identify_optimized(self, live_encoding):
    """Compare a pre-computed encoding against known faces."""
    # Same comparison logic as identify(), but skips encoding generation
```

This separates encoding generation (handled by `FrameOptimizer`) from comparison (handled by `FaceRecognizer`).

### 6.4 — Update EncodingManager to Delegate to EncodingCache

**Current:** `EncodingManager` loads encodings independently on every init.

**Change:** Keep `EncodingManager` interface unchanged for backward compatibility, but internally delegate `load_known_faces()` to `EncodingCache.get_instance()`:
```python
def load_known_faces(self):
    cache = EncodingCache.get_instance()
    cache.load(self.encoding_file)
    encodings_matrix, names = cache.get_encodings()
    self.known_encodings = list(encodings_matrix) if len(encodings_matrix) > 0 else []
    self.known_names = names
```

### 6.5 — Update encode_faces.py

After encoding generation completes and writes the new `encodings.pickle` file, trigger a cache reload so that any running recognition system picks up the new encodings:
```python
# At the end of generate_encodings()
from ai_module.optimization import EncodingCache
cache = EncodingCache.get_instance()
cache.load(ENCODING_FILE)  # Force reload with new data
```

### 6.6 — Update register_face.py

No direct changes needed to `register_face.py` since it captures images and doesn't interact with the encoding cache. However, after registration is complete, the user must run `encode_faces.py` to regenerate encodings — this is the existing workflow and remains unchanged.

## Dependencies
- Step 2 (EncodingCache must exist in `optimization.py`)
- Step 4 (FrameOptimizer must exist for the identify_optimized workflow)

## Files Modified
- `ai_module/utils.py` (FaceDetector, FaceRecognizer, EncodingManager)
- `ai_module/encode_faces.py` (add cache reload trigger)

## Expected Outcome
The utility classes are enhanced with float-precision scale-back, optimized encoding interface, and transparent cache delegation. All existing functionality remains backward-compatible.
