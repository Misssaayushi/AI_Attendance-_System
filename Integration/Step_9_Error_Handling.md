# Step 9: Error Handling & Resilience

## 🎯 Objective
Implement consistent error handling across all three pillars so that:
- Users see meaningful error messages (not stack traces)
- Network failures are handled gracefully
- The system degrades gracefully when a component is down

---

## 📝 Implementation Tasks

### Task 9.1 — Frontend Global Error Boundary

Create a React Error Boundary to catch rendering crashes:

**File**: `src/components/ErrorBoundary.jsx` (NEW)

```jsx
import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error Boundary caught:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-gray-950 flex items-center justify-center">
          <div className="text-center space-y-4">
            <h2 className="text-2xl font-bold text-red-400">Something went wrong</h2>
            <p className="text-gray-400">{this.state.error?.message || 'An unexpected error occurred'}</p>
            <button
              onClick={() => window.location.reload()}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg"
            >
              Reload Page
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

export default ErrorBoundary;
```

Wrap in `App.jsx`:
```jsx
<ErrorBoundary>
  <AuthProvider>
    <AppRoutes />
  </AuthProvider>
</ErrorBoundary>
```

---

### Task 9.2 — Frontend API Error Handler

Standardize error handling across all API calls:

**File**: `src/services/apiHelpers.js` (extend from Step 2)

```javascript
/**
 * Standard error handler for API calls.
 * Maps HTTP status codes to user-friendly messages.
 */
export const handleApiError = (error, context = '') => {
  const status = error?.response?.status;
  const detail = error?.response?.data?.detail;
  const message = error?.response?.data?.message;

  switch (status) {
    case 400:
      return detail || message || 'Invalid request. Please check your input.';
    case 401:
      return 'Session expired. Please log in again.';
    case 403:
      return 'You do not have permission to perform this action.';
    case 404:
      return `${context || 'Resource'} not found.`;
    case 409:
      return detail || 'This record already exists.';
    case 422:
      return detail || 'Validation error. Please check your input.';
    case 500:
      return 'Server error. Please try again later.';
    default:
      if (!error.response) {
        return 'Cannot connect to server. Please check if the backend is running.';
      }
      return detail || message || 'An unexpected error occurred.';
  }
};
```

---

### Task 9.3 — Frontend Connection Status Banner

Show a global banner when the Backend is unreachable:

**File**: `src/components/ConnectionStatus.jsx` (NEW)

```jsx
import { useState, useEffect } from 'react';
import { getHealthStatus } from '../services/api';

const ConnectionStatus = () => {
  const [isConnected, setIsConnected] = useState(true);

  useEffect(() => {
    const check = async () => {
      try {
        await getHealthStatus();
        setIsConnected(true);
      } catch {
        setIsConnected(false);
      }
    };

    check();
    const interval = setInterval(check, 15000);
    return () => clearInterval(interval);
  }, []);

  if (isConnected) return null;

  return (
    <div className="fixed top-0 left-0 right-0 z-50 bg-red-600 text-white text-center py-2 text-sm">
      ⚠️ Cannot connect to Backend server. Some features may be unavailable.
    </div>
  );
};

export default ConnectionStatus;
```

---

### Task 9.4 — Backend Error Response Standardization

Verify that all Backend error responses follow the same format:

```json
{
  "success": false,
  "message": "Error description",
  "detail": "Specific detail"
}
```

The Backend already has `app/middleware/error_handler.py` and `app/exceptions.py`. Verify these handle:
- `StudentNotFoundException` → 404
- `DuplicateAttendanceException` → 409
- `AttendanceVerificationException` → 400
- `DuplicateRollNumberException` → 409
- `DuplicateEmailException` → 409
- Generic `Exception` → 500

---

### Task 9.5 — AI Module Graceful Degradation

When the Backend is down, the AI Module should:
1. **Continue running** — don't crash
2. **Show "Backend Offline"** on the overlay (✅ Already implemented in `recognize_faces.py`)
3. **Log failed events** for later replay
4. **Retry** on next recognition cycle (✅ Already has retry logic in `api_service.py`)

**Enhancement**: Add a local queue that stores failed events and replays them when the Backend comes back online.

**File**: `ai-module/AI_Module/api_service.py`

```python
import json
from pathlib import Path

FAILED_EVENTS_FILE = Path(__file__).parent / "logs" / "failed_events.jsonl"

def _queue_failed_event(self, payload: AttendancePayload) -> None:
    """Store failed event for later replay."""
    try:
        with open(FAILED_EVENTS_FILE, "a") as f:
            f.write(json.dumps(payload) + "\n")
        self.logger.info("Queued failed event for student_id=%s", payload["student_id"])
    except Exception as exc:
        self.logger.error("Failed to queue event: %s", str(exc))

def replay_failed_events(self) -> int:
    """Attempt to resend previously failed events."""
    if not FAILED_EVENTS_FILE.exists():
        return 0
    
    replayed = 0
    remaining = []
    
    with open(FAILED_EVENTS_FILE, "r") as f:
        for line in f:
            try:
                payload = json.loads(line.strip())
                result = self.send_payload(payload)
                if result.success:
                    replayed += 1
                else:
                    remaining.append(line)
            except Exception:
                remaining.append(line)
    
    # Rewrite file with only remaining failed events
    with open(FAILED_EVENTS_FILE, "w") as f:
        f.writelines(remaining)
    
    return replayed
```

---

### Task 9.6 — Frontend Toast Notification for Errors

Integrate error handling with the existing `ToastContext`:

```javascript
import { useToast } from '../context/ToastContext';

// In any component:
const { showToast } = useToast();

try {
  const response = await createStudent(payload);
  showToast('Student registered successfully!', 'success');
} catch (error) {
  showToast(handleApiError(error, 'Student'), 'error');
}
```

---

## 🔄 Error Scenarios & Expected Behavior

| Scenario | Frontend Behavior | Backend Behavior | AI Module Behavior |
|---|---|---|---|
| Backend down | Shows red banner "Cannot connect" | N/A | Shows "Backend Offline" overlay, queues events |
| MySQL down | Shows "Server error" toast | Returns 500, logs DB error | Not affected directly |
| AI Module down | Dashboard shows data, no live feed | No incoming /verify requests | N/A |
| Invalid login | Shows "Login failed" error | Returns 401 | N/A |
| Duplicate attendance | Shows "Already marked" toast | Returns 409 | Shows "Cooldown" on overlay |
| Student not found | Shows "Student not found" toast | Returns 404 | Shows "Unknown Person" |
| Network timeout | Shows "Cannot connect" | Request times out | Retries, then queues |

---

## ✅ Verification Checklist
- [ ] Error Boundary catches React rendering errors
- [ ] API errors show user-friendly toast messages
- [ ] Connection status banner appears when Backend is down
- [ ] AI Module continues running when Backend is offline
- [ ] Failed events are queued and replayed when Backend recovers
- [ ] All Backend error responses follow consistent format
- [ ] No raw stack traces or technical errors shown to users

---

## 📁 Files Changed
| File | Action |
|---|---|
| `frontend/Frontend/src/components/ErrorBoundary.jsx` | **NEW** |
| `frontend/Frontend/src/components/ConnectionStatus.jsx` | **NEW** |
| `frontend/Frontend/src/services/apiHelpers.js` | **MODIFY** — add error handler |
| `frontend/Frontend/src/App.jsx` | **MODIFY** — add ErrorBoundary |
| `ai-module/AI_Module/api_service.py` | **MODIFY** — add event queue |
