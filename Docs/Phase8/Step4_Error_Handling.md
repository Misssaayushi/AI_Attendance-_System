# Step 4: Unified Error Handling UI

## Goal
Implement a premium, reusable error warning interface displaying precise system errors (e.g. webcam disabled, database down) alongside action buttons.

## Tasks
* [ ] Code the reusable `ErrorCard.jsx` module.
* [ ] Address key system failures cleanly:
  * Camera blocks / permission denied
  * Server offline / connection losses
  * Search results blank states
* [ ] Build interactive Action Buttons (e.g. Try Again reload hooks) on error cards.

## Files Affected
* `src/components/ui/ErrorCard.jsx`
* `src/pages/Attendance.jsx`
* `src/pages/Register.jsx`
