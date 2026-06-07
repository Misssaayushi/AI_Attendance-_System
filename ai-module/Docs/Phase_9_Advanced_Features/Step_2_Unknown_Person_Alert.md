# Step 2: Unknown Person Alert System

## Objective
Create `ai_module/unknown_alert.py` with a self-contained module for detecting, alerting, logging, and optionally snapshotting unknown persons. This adds a professional security layer to the recognition system.

## Why This Step
The current system only logs a warning when an unknown person is seen for too many consecutive frames (`AttendanceManager.unknown_streak`). There is no visual alert, no snapshot capture, no structured alert event, and no cooldown to prevent alert flooding. This step creates a proper alert workflow.

## Tasks

### Part A: AlertEvent Dataclass

1. Create `AlertEvent` dataclass to represent a triggered alert:
   - `timestamp: float` — time of alert trigger
   - `consecutive_frames: int` — how many frames the unknown was seen
   - `snapshot_path: Optional[str]` — file path if snapshot was saved
   - `alert_id: str` — UUID for tracing and correlation

### Part B: UnknownPersonAlertManager Class

2. Create `UnknownPersonAlertManager` class with the following:

   **Constructor** `__init__()`:
   - Initialize consecutive frame counter to 0
   - Initialize alert cooldown tracker (dict: last alert timestamp)
   - Initialize snapshot directory from config
   - Initialize statistics counters (total alerts, total snapshots)
   - Get logger instance

   **Core method** `process_unknown(frame, face_location) → AlertEvent | None`:
   - Increment consecutive unknown frame counter
   - If counter < `UNKNOWN_ALERT_CONSECUTIVE_FRAMES` → return None (not enough evidence)
   - If within cooldown window (`UNKNOWN_ALERT_COOLDOWN_SECONDS`) → return None (suppress duplicate)
   - Otherwise: create `AlertEvent`, optionally save snapshot, log alert, update cooldown tracker, return event

   **Reset method** `reset()`:
   - Called when a known person is detected (unknown streak broken)
   - Resets consecutive counter to 0
   - Does NOT reset cooldown tracker or statistics

   **Snapshot method** `_save_snapshot(frame, face_location) → str | None`:
   - Only executes if `UNKNOWN_SNAPSHOT_ENABLED` is True
   - Crops face region from frame using face_location coordinates with padding
   - Generates filename: `unknown_{timestamp}_{alert_id[:8]}.jpg`
   - Saves as JPEG with configurable quality
   - Calls `_enforce_storage_cap()` after save
   - Returns file path on success, None on failure

   **Storage cap method** `_enforce_storage_cap()`:
   - Lists all `.jpg` files in snapshot directory
   - If count > `UNKNOWN_SNAPSHOT_MAX_STORED`: delete oldest files (sorted by modification time)
   - Logs deletion events

   **Stats method** `get_alert_stats() → dict`:
   - Returns dictionary with:
     - `total_alerts_triggered`
     - `total_snapshots_saved`
     - `current_consecutive_streak`
     - `last_alert_timestamp`

## Design Details

### Alert Flow Diagram
```
Unknown Face Detected
    │
    ├── Increment consecutive counter
    │
    ├── Counter < threshold? → Return None (wait for more evidence)
    │
    ├── Within cooldown window? → Return None (suppress duplicate)
    │
    └── Threshold met + cooldown expired
        ├── Generate UUID alert_id
        ├── Save snapshot (if enabled)
        ├── Create AlertEvent
        ├── Log alert
        ├── Update cooldown timestamp
        └── Return AlertEvent
```

### Snapshot Filename Convention
```
unknown_snapshots/
├── unknown_20260601_093500_a1b2c3d4.jpg
├── unknown_20260601_094215_e5f6g7h8.jpg
└── unknown_20260601_095030_i9j0k1l2.jpg
```

### Relationship with Existing Code
- The existing `AttendanceManager.unknown_streak` logic in `utils.py` is **preserved unchanged**
- `UnknownPersonAlertManager` operates at a **higher level** — it wraps around the recognition results
- The alert manager is called from `recognize_faces.py` after the existing verification logic runs
- No changes to `AttendanceManager` are required for this step

## Dependencies
- Step 1 (config values: `UNKNOWN_ALERT_*`, `UNKNOWN_SNAPSHOT_*`)

## Files Created
- `ai_module/unknown_alert.py`

## Expected Outcome
A standalone module that can be imported and used with a single method call per frame. When an unknown person is detected for enough consecutive frames, an `AlertEvent` is produced with an optional face snapshot. The system never floods logs — alerts are suppressed during cooldown periods. Snapshot storage is capped to prevent disk exhaustion.
