# Phase 4: Attendance Page UI — Implementation Plan

## 1. Attendance Workflow Architecture
- **Stage 1 (Passive)**: System waiting for face detection.
- **Stage 2 (Active)**: Face detected, "Scanning..." state triggered.
- **Stage 3 (Processing)**: Mock delay simulating backend matching.
- **Stage 4 (Feedback)**: One of 4 results shown (Success, Already Marked, Unknown, Error).

## 2. Live Recognition UI Strategy
- **Webcam Interface**: Reusable `WebcamFeed` with a persistent scanningHUD.
- **Face Detection Box**: A dynamic SVG overlay that pulses to indicate "Focus."
- **Scanline**: CSS animation across the feed to enhance the "AI" feel.

## 3. Attendance Status System (4 States)
1.  **Success** (Green): "Attendance Marked Successfully" + Student Name + Time.
2.  **Duplicate** (Orange): "Attendance Already Marked."
3.  **Unknown** (Red): "Unknown Person Detected."
4.  **Scanning** (Blue): "Scanning Face..." with loading pulse.

## 4. Component Breakdown
- `AttendanceHUD`: Main container.
- `DetectionOverlay`: SVG box and scanline.
- `StatusPanel`: The 4-state feedback card.
- `StatsDashboard`: Mini cards for Today's Stats.
- `ActivityFeed`: Scrolling log of recognition events.

## 5. State Management
```javascript
{
  isScanning: false,
  recognitionState: 'idle', // idle | scanning | success | duplicate | unknown
  matchedStudent: null,
  attendanceStats: { present: 42, total: 150, percent: 28 },
  logs: []
}
```

## 6. Error Handling Strategy
- **Permissions**: Alert for camera access.
- **No Face**: Show "No Face Detected" warning if scanner stays idle for too long.
- **Multi-Face**: Show "Multiple Faces Detected" warning.
