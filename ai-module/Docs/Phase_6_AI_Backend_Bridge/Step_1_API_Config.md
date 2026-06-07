# Step 1: API Configuration

## Objective
Update `ai_module/config.py` with all settings required by the AI-backend communication layer.

## Why This Step Comes First
The API service and recognition loop should not hardcode URLs, endpoint paths, timeouts, or mock mode flags. Central configuration keeps Phase 6 easy to test and safe to change.

## Tasks
1. Add backend connection settings:
   - `API_BASE_URL`
   - `ATTENDANCE_VERIFY_ENDPOINT`
   - `ATTENDANCE_VERIFY_URL`

2. Add request reliability settings:
   - `API_TIMEOUT_SECONDS`
   - `API_RETRY_COUNT`
   - `API_RETRY_DELAY_SECONDS`

3. Add mock mode settings:
   - `API_MOCK_MODE`
   - `API_MOCK_FORCE_FAILURE`
   - `API_MOCK_RESPONSE_DELAY_SECONDS`

4. Add response display settings:
   - `API_FEEDBACK_DISPLAY_SECONDS`
   - `API_SUCCESS_MESSAGE`
   - `API_ERROR_MESSAGE`

5. Keep default values development-friendly:
   - Base URL should point to local FastAPI, for example `http://127.0.0.1:8000`.
   - Endpoint should remain `/api/v1/attendance/verify`.
   - Timeout should be short enough to protect webcam FPS.

## Expected Config Shape
The final implementation should support this behavior:
- Production mode sends real HTTP requests.
- Mock mode bypasses the backend.
- Network errors return readable status messages instead of exceptions.

## Expected Outcome
`config.py` becomes the single place to change backend connectivity and testing behavior for Phase 6.

