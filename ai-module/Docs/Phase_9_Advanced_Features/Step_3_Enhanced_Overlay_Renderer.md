# Step 3: Enhanced Overlay Renderer

## Objective
Create `ai_module/overlay_renderer.py` with a dedicated rendering engine that replaces ad-hoc `draw_face_box` and inline `putText` calls with a professional, state-aware overlay system featuring confidence bars, status badges, animated borders, and a system HUD.

## Why This Step
The current overlay system consists of a basic `FrameUtils.draw_face_box()` method that draws a simple rectangle with a text label, plus a hardcoded `_draw_status_legend()` function. For a university demo, the visual presentation needs to look professional — with color-coded states, confidence indicators, and a clean system dashboard.

## Tasks

### Part A: OverlayRenderer Class

1. Create `OverlayRenderer` class with the following:

   **Constructor** `__init__()`:
   - Load overlay preferences from config (font scale, border thickness, animation toggle)
   - Initialize animation frame counter
   - Initialize verification animation tracker (dict: student_id → animation_start_frame)
   - Define color palette constants

2. **Color palette** (consistent BGR values):

   | State | Box Color (BGR) | Label |
   |-------|-----------------|-------|
   | Verified | `(0, 200, 83)` — Emerald Green | ✓ Verified |
   | Cooldown | `(0, 191, 255)` — Amber/Gold | ⏳ Cooldown |
   | Pending/Stability | `(255, 191, 0)` — Sky Blue | ◉ Verifying |
   | Unknown | `(0, 0, 220)` — Alert Red | ⚠ Unknown |
   | Low Confidence | `(0, 140, 255)` — Orange | ◈ Low Conf |

### Part B: Face Overlay Method

3. **Master method** `draw_face_overlay(frame, face_loc, name, confidence, status, api_status, is_unknown, cooldown_remaining, frame_count)`:
   - Draws face bounding box with state-appropriate color
   - Draws name label with background
   - Draws confidence percentage text
   - Calls `draw_confidence_bar()` if enabled
   - Calls `draw_status_badge()` with appropriate state
   - Calls `draw_animated_border()` if recently verified and animations enabled
   - Calls `draw_timestamp_label()` if enabled
   - Draws cooldown remaining text if applicable

### Part C: Confidence Bar

4. **Method** `draw_confidence_bar(frame, x, y, width, confidence, color)`:
   - 80px wide × 8px tall horizontal bar rendered below face box
   - Background: dark gray outline
   - Fill: proportional to confidence percentage
   - Color gradient: red (< 80%) → yellow (80–90%) → green (> 90%)
   - Renders cleanly at all confidence values (0–100%)

### Part D: Status Badge

5. **Method** `draw_status_badge(frame, x, y, text, bg_color)`:
   - Pill-shaped rounded rectangle background
   - White text centered inside
   - Compact size: auto-sized based on text length
   - Used for: "✓ Verified", "⏳ Cooldown", "⚠ Unknown", "◉ Verifying", "◈ Low Conf"

### Part E: Animated Border

6. **Method** `draw_animated_border(frame, face_loc, color, frame_count)`:
   - Pulsing border effect on successful verification
   - Uses `sin(frame_count * 0.15)` mapped to thickness range `[2, 4]`
   - Triggers only for 30 frames after a successful verification event
   - After 30 frames: reverts to static border
   - Performance: adds ~0.1ms per face — negligible cost

### Part F: Timestamp Label

7. **Method** `draw_timestamp_label(frame, x, y)`:
   - Small text showing current time: "HH:MM:SS"
   - Rendered below the face label area
   - Uses compact font size (0.4 scale)
   - Only shown when `OVERLAY_SHOW_TIMESTAMP` is True

### Part G: System HUD

8. **Method** `draw_system_hud(frame, fps, avg_fps, face_count, session_stats)`:
   - Replaces the existing `_draw_status_legend()` function
   - Semi-transparent dark panel in top-right corner
   - Content layout:
     ```
     ┌─────────────────────────────┐
     │  AI ATTENDANCE SYSTEM       │
     │  FPS: 22.3 | Faces: 3      │
     │  Verified: 12 | Unknown: 2 │
     │  Session: 00:15:32         │
     └─────────────────────────────┘
     ```
   - Green text for healthy metrics, amber for warnings
   - Updates every frame with latest stats

### Part H: Unknown Warning Banner

9. **Method** `draw_unknown_warning_banner(frame, alert_event)`:
   - Full-width red banner across the top of the frame
   - Text: "⚠ UNKNOWN PERSON DETECTED"
   - Semi-transparent red background
   - Shown only when an active `AlertEvent` exists
   - Auto-hides after the alert cooldown expires

## Design Details

### Performance Considerations
- All rendering uses direct OpenCV drawing functions (no external libraries)
- Semi-transparent panels use localized ROI copy with `cv2.addWeighted`, not full-frame copy
- Color calculations are done once in constructor, not per-frame
- Animation calculations use simple `sin()` — no complex math per frame

### Overlay Layering Order
```
1. Face bounding boxes (bottom layer)
2. Confidence bars
3. Name labels and status badges
4. Animated borders (on top of boxes)
5. Timestamp labels
6. Unknown warning banner (top layer)
7. System HUD (top-right, always on top)
```

### Backward Compatibility
- Existing `FrameUtils.draw_face_box()` is **not modified** — it remains available
- Existing `_draw_status_legend()` function is **not deleted** — it's replaced in the main loop
- `OverlayRenderer` is a new, independent class that can be toggled on/off

## Dependencies
- Step 1 (config values: `OVERLAY_*`)
- Step 8 (visual utility methods in `FrameUtils` — but can use basic OpenCV directly if Step 8 isn't done yet)

## Files Created
- `ai_module/overlay_renderer.py`

## Expected Outcome
A professional overlay rendering engine that transforms the webcam feed from a basic bounding-box display into a polished, state-aware visualization. Face boxes are color-coded by recognition state, confidence is shown both as text and as a visual bar, status badges clearly communicate the verification state, and a clean system HUD provides real-time metrics. The visual quality is suitable for a professional university demo.
