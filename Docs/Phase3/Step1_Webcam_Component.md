# Step 1: Reusable Webcam Component

## Goal
Build the `WebcamFeed.jsx` component that provides a live preview and capture capabilities.

## Tasks
- [x] Create `src/components/register/WebcamFeed.jsx`.
- [x] Implement `startCamera` logic using `navigator.mediaDevices`.
- [x] Implement `stopCamera` logic (stopping all tracks).
- [x] Create the visual "Frame" styling for the camera preview.
- [x] Add "Start", "Stop", and "Capture" buttons with Lucide icons.
- [x] Handle permission errors with a simple callback to the parent.

## UI Specs
- Aspect Ratio: 16:9 or 4:3.
- Placeholder: A dark card with a "Camera" icon when inactive.
- Overlay: A subtle guide overlay for face positioning.
