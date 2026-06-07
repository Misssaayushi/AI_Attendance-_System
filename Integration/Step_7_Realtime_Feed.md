# Step 7: Real-Time Attendance Feed (WebSocket)

## 🎯 Objective
Add real-time live updates to the Frontend when the AI Module marks attendance, so the Dashboard and Attendance Terminal show instant feedback without polling.

---

## 📊 Current State
- Frontend uses **no real-time mechanism** — Dashboard polls every 30 seconds (Step 5)
- Backend has **no WebSocket support** — only REST endpoints
- AI Module sends HTTP POST to Backend and gets a response, but Frontend has no way to know it happened in real-time

---

## 📝 Implementation Tasks

### Task 7.1 — Add WebSocket Support to Backend

**Install dependency**: `pip install websockets`

**File**: `backend/Backend/app/routes/websocket.py` (NEW)

```python
from __future__ import annotations

import asyncio
import json
from typing import Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.utils.logger import logger

router = APIRouter()

# Global set of active WebSocket connections
active_connections: Set[WebSocket] = set()


@router.websocket("/ws/attendance")
async def attendance_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for real-time attendance event streaming.
    Frontend connects here to receive instant attendance notifications.
    """
    await websocket.accept()
    active_connections.add(websocket)
    logger.info("event=websocket_connected total_connections=%s", len(active_connections))
    
    try:
        while True:
            # Keep connection alive — wait for client pings
            data = await websocket.receive_text()
            # Client can send "ping" to keep alive
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        active_connections.discard(websocket)
        logger.info("event=websocket_disconnected total_connections=%s", len(active_connections))


async def broadcast_attendance_event(event: dict):
    """
    Broadcast an attendance event to all connected WebSocket clients.
    Called from the /verify endpoint after successful attendance marking.
    """
    if not active_connections:
        return
    
    message = json.dumps(event)
    disconnected = set()
    
    for connection in active_connections:
        try:
            await connection.send_text(message)
        except Exception:
            disconnected.add(connection)
    
    active_connections.difference_update(disconnected)
```

---

### Task 7.2 — Register WebSocket Router in main.py

**File**: `backend/Backend/app/routes/__init__.py`

```diff
+from app.routes.websocket import router as ws_router
 
 api_router.include_router(health_router, prefix="/health", tags=["System Health"])
 ...
+api_router.include_router(ws_router, tags=["WebSocket"])
```

---

### Task 7.3 — Broadcast from /verify Endpoint

When the AI Module successfully marks attendance, broadcast the event to all WebSocket clients.

**File**: `backend/Backend/app/routes/attendance.py`

```diff
+import asyncio
+from app.routes.websocket import broadcast_attendance_event

 @router.post("/verify", status_code=status.HTTP_201_CREATED)
 def verify_attendance_from_ai(payload, x_api_key, db):
     ...
     record = attendance_service.mark_attendance(db, mark_request)
+    
+    # Broadcast real-time event to all connected Frontend clients
+    event = {
+        "type": "attendance_marked",
+        "student_id": record.student_id,
+        "student_name": record.student.full_name if record.student else payload.name,
+        "status": record.status,
+        "time": record.time.isoformat() if record.time else None,
+        "confidence": payload.confidence,
+    }
+    asyncio.create_task(broadcast_attendance_event(event))
     
     return success_response(...)
```

---

### Task 7.4 — Add WebSocket Client to Frontend

**File**: `src/services/websocket.js` (NEW)

```javascript
class AttendanceWebSocket {
  constructor() {
    this.ws = null;
    this.listeners = new Set();
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 10;
    this.reconnectDelay = 2000;
  }

  connect() {
    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/api/v1/ws/attendance';
    
    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log('🔗 WebSocket connected');
      this.reconnectAttempts = 0;
      
      // Ping every 30 seconds to keep alive
      this.pingInterval = setInterval(() => {
        if (this.ws?.readyState === WebSocket.OPEN) {
          this.ws.send('ping');
        }
      }, 30000);
    };

    this.ws.onmessage = (event) => {
      if (event.data === 'pong') return;
      
      try {
        const data = JSON.parse(event.data);
        this.listeners.forEach(listener => listener(data));
      } catch (err) {
        console.warn('WebSocket message parse error:', err);
      }
    };

    this.ws.onclose = () => {
      console.log('🔌 WebSocket disconnected');
      clearInterval(this.pingInterval);
      this.attemptReconnect();
    };

    this.ws.onerror = (err) => {
      console.error('WebSocket error:', err);
    };
  }

  attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = this.reconnectDelay * Math.min(this.reconnectAttempts, 5);
      console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})...`);
      setTimeout(() => this.connect(), delay);
    }
  }

  subscribe(listener) {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  disconnect() {
    clearInterval(this.pingInterval);
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

// Singleton instance
export const attendanceWS = new AttendanceWebSocket();
```

---

### Task 7.5 — Create React Hook for WebSocket Events

**File**: `src/hooks/useAttendanceFeed.js` (NEW)

```javascript
import { useState, useEffect } from 'react';
import { attendanceWS } from '../services/websocket';

export function useAttendanceFeed() {
  const [latestEvent, setLatestEvent] = useState(null);
  const [eventHistory, setEventHistory] = useState([]);

  useEffect(() => {
    attendanceWS.connect();

    const unsubscribe = attendanceWS.subscribe((event) => {
      if (event.type === 'attendance_marked') {
        setLatestEvent(event);
        setEventHistory(prev => [event, ...prev].slice(0, 50)); // Keep last 50
      }
    });

    return () => {
      unsubscribe();
      attendanceWS.disconnect();
    };
  }, []);

  return { latestEvent, eventHistory };
}
```

---

### Task 7.6 — Integrate into Dashboard ActivityFeed

**File**: `src/components/dashboard/ActivityFeed.jsx`

```javascript
import { useAttendanceFeed } from '../../hooks/useAttendanceFeed';

const ActivityFeed = () => {
  const { latestEvent, eventHistory } = useAttendanceFeed();
  
  // Show toast notification on new event
  useEffect(() => {
    if (latestEvent) {
      showToast(`✅ ${latestEvent.student_name} marked ${latestEvent.status}`);
    }
  }, [latestEvent]);

  return (
    <div>
      {eventHistory.map((event, idx) => (
        <div key={idx} className="...">
          <span>{event.student_name}</span>
          <span>{event.status}</span>
          <span>{event.time}</span>
        </div>
      ))}
    </div>
  );
};
```

---

## 🔄 Real-Time Flow (After Integration)

```
1. AI Module recognizes "Rahul Sharma" → sends POST /verify to Backend
2. Backend marks attendance in MySQL
3. Backend broadcasts WebSocket event: { type: "attendance_marked", student_name: "Rahul Sharma", ... }
4. All connected Frontend clients receive the event instantly
5. Dashboard ActivityFeed shows "✅ Rahul Sharma marked Present" in real-time
6. Toast notification appears
7. Dashboard stats auto-update
```

---

## ✅ Verification Checklist
- [ ] Backend WebSocket endpoint `/ws/attendance` accepts connections
- [ ] AI Module's `/verify` POST triggers WebSocket broadcast
- [ ] Frontend WebSocket client connects and receives events
- [ ] Dashboard ActivityFeed updates in real-time
- [ ] Toast notification appears on new attendance event
- [ ] WebSocket auto-reconnects on disconnection
- [ ] Multiple browser tabs all receive events simultaneously

---

## 📁 Files Changed
| File | Action |
|---|---|
| `backend/Backend/app/routes/websocket.py` | **NEW** |
| `backend/Backend/app/routes/__init__.py` | **MODIFY** — register WebSocket router |
| `backend/Backend/app/routes/attendance.py` | **MODIFY** — add broadcast call |
| `frontend/Frontend/src/services/websocket.js` | **NEW** |
| `frontend/Frontend/src/hooks/useAttendanceFeed.js` | **NEW** |
| `frontend/Frontend/src/components/dashboard/ActivityFeed.jsx` | **MODIFY** |
| `frontend/Frontend/.env` | **MODIFY** — add `VITE_WS_URL` |
