# Step 8: Visual Enhancement Utilities

## Objective
Extend the existing `FrameUtils` class in `ai_module/utils.py` with professional rendering helpers — rounded rectangles, gradient bars, semi-transparent panels, pulsing borders, and a centralized color theme — used by the `OverlayRenderer` (Step 3) and other visualization components.

## Why This Step
The `OverlayRenderer` needs utility functions for professional rendering that don't belong in the renderer itself. These are generic visual primitives that could be reused across multiple components. Adding them to the existing `FrameUtils` class keeps the architecture consistent with the established pattern.

## Tasks

### Part A: Rounded Rectangle

1. Add static method `draw_rounded_rect(frame, pt1, pt2, color, radius=10, thickness=1, fill=False)`:
   - Draws a rectangle with rounded corners using OpenCV primitives
   - `pt1` and `pt2` are top-left and bottom-right corner tuples
   - If `fill=True`: filled rectangle with rounded corners
   - If `fill=False`: outline only
   - Implementation uses `cv2.rectangle` for the center body + `cv2.circle` for corners + `cv2.rectangle` for side fills
   - Handles edge case where radius > half of width/height by capping

### Part B: Gradient Bar

2. Add static method `draw_gradient_bar(frame, x, y, width, height, value, max_value=100.0)`:
   - Draws a horizontal progress bar with color gradient
   - Background: dark gray `(40, 40, 40)` full-width bar
   - Foreground: filled proportionally to `value / max_value`
   - Color interpolation based on fill percentage:
     - 0–50%: Red `(0, 0, 200)` → Yellow `(0, 200, 200)`
     - 50–100%: Yellow `(0, 200, 200)` → Green `(0, 200, 0)`
   - Thin white outline border
   - Handles edge cases: value < 0 (clamp to 0), value > max_value (clamp to max)

### Part C: Semi-Transparent Panel

3. Add static method `draw_semi_transparent_panel(frame, x, y, w, h, color=(0, 0, 0), alpha=0.6)`:
   - Creates a semi-transparent overlay rectangle
   - Uses localized ROI approach for performance (not full-frame copy):
     ```python
     # Clamp coordinates to frame boundaries
     roi = frame[y:y+h, x:x+w]
     overlay = roi.copy()
     cv2.rectangle(overlay, (0, 0), (w, h), color, cv2.FILLED)
     cv2.addWeighted(overlay, alpha, roi, 1 - alpha, 0, roi)
     ```
   - Returns the frame (modified in-place)
   - Handles edge cases: coordinates out of bounds (clamp to frame dimensions)

### Part D: Pulsing Border

4. Add static method `draw_pulsing_border(frame, face_loc, color, intensity, thickness_range=(2, 4))`:
   - Draws a face bounding box with variable thickness
   - `intensity` is a float 0.0–1.0 controlling the pulse (typically from `sin()`)
   - Actual thickness = `thickness_range[0] + intensity * (thickness_range[1] - thickness_range[0])`
   - Uses `cv2.rectangle` with computed integer thickness
   - Simple and efficient — single rectangle draw call

### Part E: Centralized Color Theme

5. Add static method `get_state_color(state_name) → tuple`:
   - Returns BGR color tuple for a given recognition state
   - Centralized color lookup to ensure consistent theming:
   
   | State Name | BGR Color | Description |
   |-----------|-----------|-------------|
   | `"verified"` | `(0, 200, 83)` | Emerald green |
   | `"cooldown"` | `(0, 191, 255)` | Amber/gold |
   | `"pending"` | `(255, 191, 0)` | Sky blue |
   | `"unknown"` | `(0, 0, 220)` | Alert red |
   | `"low_confidence"` | `(0, 140, 255)` | Orange |
   | `"error"` | `(0, 0, 255)` | Pure red |
   | `"neutral"` | `(180, 180, 180)` | Light gray |
   
   - Returns `(180, 180, 180)` (neutral gray) for unrecognized state names
   - Dictionary is defined as a class-level constant for zero per-call overhead

## Design Details

### Performance Considerations
- **Rounded rectangle**: Uses 4 circles + 3 rectangles = 7 OpenCV calls. ~0.05ms per call — acceptable for badges
- **Gradient bar**: Single rectangle draw + one color computation. ~0.02ms
- **Semi-transparent panel**: Uses ROI copy (localized area only, not full frame). Cost proportional to panel size. For a 300×150px panel: ~0.1ms
- **Pulsing border**: Single rectangle draw. ~0.01ms
- **Color lookup**: Dictionary access. ~0 overhead

### Why Static Methods
All methods are stateless — they operate purely on the input frame and parameters. This matches the existing `FrameUtils` pattern (`resize_frame`, `add_text_overlay`, `draw_face_box` are all static).

### Edge Case Handling
- All methods clamp coordinates to frame boundaries to prevent OpenCV errors
- All methods handle None/empty frames gracefully (return immediately)
- Gradient bar handles negative values and values exceeding max

## Dependencies
- None. These are standalone utility methods.
- Used by: Step 3 (OverlayRenderer), Step 9 (main loop integration)

## Files Modified
- `ai_module/utils.py` (add methods to existing `FrameUtils` class)

## Expected Outcome
`FrameUtils` gains a suite of professional rendering primitives that the `OverlayRenderer` and other components can use. All methods are consistent with the existing static-method pattern, handle edge cases gracefully, and have minimal performance overhead. The centralized color theme ensures visual consistency across all overlays.
