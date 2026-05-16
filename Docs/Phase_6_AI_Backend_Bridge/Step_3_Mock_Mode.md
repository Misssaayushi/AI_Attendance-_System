# Step 3: Mock Mode

## Objective
Build a mock mode switch so the AI module can verify API-side logic without a live FastAPI backend.

## Main Responsibility
Mock mode should behave like the backend from the AI module's point of view. It should return structured success or failure responses while keeping the recognition loop unchanged.

## Tasks
1. Read mock settings from `config.py`.
   - `API_MOCK_MODE`
   - `API_MOCK_FORCE_FAILURE`
   - `API_MOCK_RESPONSE_DELAY_SECONDS`

2. Add mock handling inside `AttendanceAPIService`.
   - If mock mode is enabled, skip the real HTTP request.
   - Return a success response by default.
   - Return a failure response when `API_MOCK_FORCE_FAILURE=True`.

3. Preserve payload validation in mock mode.
   - Confirm required fields exist.
   - Confirm confidence is numeric.
   - Confirm timestamp is present.

4. Log mock transmissions.
   - Use logger name `API_Connector`.
   - Clearly mark logs as mock mode.

5. Keep mock mode transparent to `recognize_faces.py`.
   - Recognition code should call the same service method in real and mock modes.
   - Only the service decides whether to call the real backend.

## Example Mock Results
- Success: `Mock Success: Attendance Logged`
- Failure: `Mock Failure: Backend Rejected Event`

## Expected Outcome
The AI developer can test Phase 6 behavior, overlay messages, cooldown protection, and failure handling without starting the backend.

