# Phase 3: Registration Page UI — Implementation Plan

## 1. Registration Workflow Architecture
The page will follow a logical flow:
1.  **Camera Access**: User starts the camera and positions themselves.
2.  **Face Capture**: User captures their face; system validates capture (mock) and unlocks the form.
3.  **Details Entry**: User fills in the 10 student fields.
4.  **Review & Submit**: User submits the data; a success toast appears and the form resets.

## 2. Webcam Integration Strategy
- **API**: Use browser-native `navigator.mediaDevices.getUserMedia`.
- **Display**: Render stream into a `<video>` element.
- **Capture**: Draw current video frame to a hidden `<canvas>` and convert to a data URL for preview.
- **Cleanup**: Ensure camera tracks are stopped when the component unmounts or the "Stop Camera" button is clicked.

## 3. Form Handling & Validation
- **State**: Controlled components using a single `formData` object.
- **Validation**: 
  - Real-time visual feedback (red borders/text).
  - Validation rules: 
    - Full Name: Required, min 3 chars.
    - Roll Number: Required, unique format.
    - Email: Regex check.
    - Contact: Numeric check.
    - Selects: Must not be empty.

## 4. Component Breakdown
- `RegistrationPage`: Main page container.
- `WebcamFeed`: Handles camera stream and frame capture.
- `RegisterForm`: Modular form component.
- `StatusBadge`: Shows "Camera Ready", "Face Captured", etc.
- `Alert`: Reusable error/warning notification.

## 5. State Management Plan
```javascript
{
  stream: null,            // MediaStream object
  isCameraActive: false,   // UI toggle
  capturedImage: null,     // Base64 string for preview
  isFaceCaptured: false,   // Unlock form trigger
  formData: { ... },       // 10 student fields
  formErrors: { ... },     // Field-specific errors
  status: 'idle',          // idle | success | error | loading
}
```

## 6. Error Handling Flow
- **Permission Denied**: Detect `NotAllowedError` and show a friendly UI alert.
- **No Device**: Detect `NotFoundError` if no camera is plugged in.
- **Validation Failure**: Prevent submission and scroll to the first error.

## 7. Future Backend Preparation
- The `capturedImage` will be stored as a Base64 string, ready to be sent as a file or string to the FastAPI backend.
- Form data structure matches the expected Pydantic models for the backend.
