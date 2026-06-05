# Step 9: Recognition Loop Integration

## Objective
Wire all Phase 9 components into the main `start_recognition()` function in `ai_module/recognize_faces.py` — integrating unknown alerts, enhanced overlays, activity logging, security tracking, and session report generation while preserving all existing functionality.

## Why This Step
This is the final assembly step. All individual components (Steps 2–8) are standalone and tested. This step connects them into the existing recognition pipeline. It comes last to minimize risk — if any component fails, the existing system continues to work.

## Tasks

### Part A: New Imports

1. Add imports for Phase 9 modules:
   ```python
   from unknown_alert import UnknownPersonAlertManager
   from overlay_renderer import OverlayRenderer
   from activity_monitor import ActivityMonitor
   from error_handler import SecurityMonitor
   ```

2. Add new config imports:
   ```python
   from config import (
       ANALYTICS_SESSION_REPORT_ON_EXIT,
       OVERLAY_ANIMATION_ENABLED,
       UNKNOWN_LABEL,
       # ... existing imports preserved
   )
   ```

### Part B: Component Initialization

3. Add Phase 9 component initialization after existing setup (after line ~258):
   ```python
   # Phase 9: Advanced Features
   unknown_alert_mgr = UnknownPersonAlertManager()
   overlay_renderer = OverlayRenderer()
   activity_monitor = ActivityMonitor()
   security_monitor = SecurityMonitor()
   active_alert_event = None  # Current unknown person alert
   ```

### Part C: Face Processing Integration

4. Inside the face processing loop (`for face_loc in face_locations:`), after existing recognition and verification logic:

   **After recognition result** (after name and confidence are determined):
   ```python
   # Phase 9: Activity logging
   activity_monitor.log_recognition(student_id, name, confidence, verified)
   
   # Phase 9: Security monitoring
   security_monitor.track_recognition_attempt(
       student_id, confidence, verified, face_location=face_loc
   )
   ```

   **If unknown face detected** (where `name == UNKNOWN_LABEL`):
   ```python
   # Phase 9: Unknown person alert
   alert_event = unknown_alert_mgr.process_unknown(frame, face_loc)
   if alert_event:
       active_alert_event = alert_event
       activity_monitor.log_unknown_detection(alert_event)
   else:
       activity_monitor.log_unknown_detection()
   ```

   **If known face detected**:
   ```python
   # Phase 9: Reset unknown streak
   unknown_alert_mgr.reset()
   ```

   **If cooldown blocked**:
   ```python
   # Phase 9: Log cooldown event
   cooldown_remaining = attendance_manager.get_cooldown_remaining(student_id)
   activity_monitor.log_cooldown_event(student_id, cooldown_remaining)
   ```

### Part D: Overlay Rendering Replacement

5. Replace the existing overlay section (lines ~388–433) with Phase 9 overlay rendering:

   **Face overlays** — replace `FrameUtils.draw_face_box()` calls:
   ```python
   for (face_loc, name, conf, status_tuple) in zip(...):
       is_unknown = (name == UNKNOWN_LABEL)
       cooldown_remaining = attendance_manager.format_cooldown_remaining(student_id)
       
       overlay_renderer.draw_face_overlay(
           frame, face_loc, name, conf,
           verification_status, api_status,
           is_unknown, cooldown_remaining, frame_count
       )
   ```

   **System HUD** — replace `_draw_status_legend()` and existing text overlays:
   ```python
   session_stats = activity_monitor.get_analytics_summary(perf_tracker)
   overlay_renderer.draw_system_hud(
       frame, perf_tracker.get_fps(), perf_tracker.get_avg_fps(),
       len(face_locations), session_stats
   )
   ```

   **Unknown warning banner** — add after system HUD:
   ```python
   if active_alert_event:
       overlay_renderer.draw_unknown_warning_banner(frame, active_alert_event)
       # Clear alert after display cooldown
       if time.time() - active_alert_event.timestamp > UNKNOWN_ALERT_COOLDOWN_SECONDS:
           active_alert_event = None
   ```

6. Keep the "Press ESC to Quit" overlay (existing line ~428)

### Part E: Cleanup and Report Generation

7. Enhance the `finally` block with Phase 9 cleanup:
   ```python
   finally:
       # Phase 9: Generate session report
       if ANALYTICS_SESSION_REPORT_ON_EXIT:
           try:
               report_path = activity_monitor.export_session_report(
                   perf_tracker=perf_tracker if 'perf_tracker' in locals() else None
               )
               logger.info(f"Session report saved: {report_path}")
           except Exception as e:
               logger.warning(f"Failed to generate session report: {e}")
       
       # Phase 9: Cleanup
       if 'activity_monitor' in locals():
           activity_monitor.cleanup()
       if 'security_monitor' in locals():
           security_monitor.cleanup()
       
       # Existing cleanup (preserved)
       if 'api_dispatcher' in locals():
           api_dispatcher.cleanup(timeout=2.0)
       if 'cam' in locals():
           cam.cleanup()
   ```

### Part F: Logger Branding Update

8. Update the initialization log message:
   - Current: `"Initializing Optimized Face Recognition System (Phase 7)..."`
   - Updated: `"Initializing AI Attendance Recognition System (Phase 9 — Production)..."`

## Design Details

### Integration Strategy: Additive, Not Destructive
- All existing helper functions (`_resolve_api_feedback`, `_resolve_verification_color`, `_short_verification_status`, `_short_api_status`) are **kept** — they're still used by the rendering logic internally
- The `_draw_status_legend()` function is **not deleted** — its call is replaced with `overlay_renderer.draw_system_hud()`
- If `OverlayRenderer` fails to import (e.g., file not yet created), the system falls back to existing rendering

### Graceful Degradation
```python
try:
    from overlay_renderer import OverlayRenderer
    _HAS_OVERLAY_RENDERER = True
except ImportError:
    _HAS_OVERLAY_RENDERER = False
```
This allows the system to run even if Phase 9 modules aren't present — useful during incremental development.

### Frame Count for Animations
- The existing `frame_count` variable (line ~261, ~456) is passed to `overlay_renderer.draw_face_overlay()` for animation timing
- No new counter needed — reuses existing infrastructure

### Performance
- Phase 9 adds ~2–3ms per frame of processing
- Most of this is overlay rendering (which replaces existing rendering, so net new cost is ~1ms)
- Analytics and monitoring calls are < 0.5ms total

## Dependencies
- Step 2 (UnknownPersonAlertManager)
- Step 3 (OverlayRenderer)
- Step 4 (enhanced AttendanceManager with cooldown remaining)
- Step 5 + Step 6 (ActivityMonitor with analytics)
- Step 7 (SecurityMonitor)
- Step 8 (visual utility methods)

## Files Modified
- `ai_module/recognize_faces.py` (significant modifications to `start_recognition()`)

## Expected Outcome
The main recognition loop now integrates all Phase 9 components:
- Unknown persons trigger visual alerts and snapshot captures
- Face overlays show professional confidence bars and status badges
- Activity is logged to JSONL for post-session analysis
- Security patterns are monitored and flagged
- A session report is auto-generated on exit
- All existing functionality is preserved — the system runs identically if Phase 9 modules aren't available
