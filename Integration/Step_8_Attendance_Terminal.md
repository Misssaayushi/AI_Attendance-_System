# Step 8: Attendance Terminal AI Integration

## 🎯 Objective
Transform the Frontend's Attendance Terminal page from a **simulation-only** UI into a **real** attendance terminal that can:
1. Display the AI Module's recognition status in real-time
2. Show live attendance events as they happen
3. Provide actual stats instead of hardcoded numbers

---

## 📊 Current State

### Attendance.jsx (❌ Simulation Only)
- WebcamFeed opens camera but does **NO recognition** — it's just a video preview
- "Match", "Duplicate", "Unknown" buttons **simulate** events with `setTimeout`
- Activity feed shows only simulated logs
- Stats show hardcoded values (`42 + logs.filter(...)`, `94%`)
- AI Module runs as a **separate desktop process** with its own OpenCV window

---

## 📝 Architecture Decision

The AI Module uses **OpenCV's `cv2.imshow()`** which requires a desktop GUI window. It cannot run inside a browser. There are two integration approaches:

### Option A: Browser-as-Monitor (Recommended for Presentation)
- AI Module continues running as a separate desktop process
- Frontend monitors attendance events via WebSocket (from Step 7)
- Frontend shows real-time stats and activity feed from actual AI detections
- Camera feed in the browser is **for display only** (or removed in favor of focusing on the AI window)

### Option B: Full Browser Integration (Complex, Future)
- AI Module exposes a video streaming API (MJPEG or WebRTC)
- Frontend renders the AI-processed video frames
- Requires significant AI Module refactoring

**We'll implement Option A** — it's practical and presentation-ready.

---

## 📝 Implementation Tasks

### Task 8.1 — Remove Simulation Logic

Remove the `triggerSimulation()` function and the simulation buttons. Replace with real-time data:

```diff
-const triggerSimulation = (type) => { ... };

-<Button onClick={() => triggerSimulation('success')}>Match</Button>
-<Button onClick={() => triggerSimulation('duplicate')}>Duplicate</Button>
-<Button onClick={() => triggerSimulation('unknown')}>Unknown</Button>
```

---

### Task 8.2 — Connect to WebSocket Feed

Use the `useAttendanceFeed` hook from Step 7:

```javascript
import { useAttendanceFeed } from '../hooks/useAttendanceFeed';

const Attendance = () => {
  const { latestEvent, eventHistory } = useAttendanceFeed();
  
  // Transform WebSocket events into log format
  const logs = eventHistory.map((event, idx) => ({
    id: idx,
    name: event.student_name,
    message: event.status === 'Present' ? 'Attendance Marked' : event.status,
    type: event.status === 'Present' ? 'success' : 'unknown',
    time: event.time ? new Date('1970-01-01T' + event.time).toLocaleTimeString([], 
      { hour: '2-digit', minute: '2-digit' }) : '',
    confidence: event.confidence,
  }));
  
  // Update recognition state based on latest event
  useEffect(() => {
    if (latestEvent) {
      setRecognitionState('success');
      setLastMatch({ name: latestEvent.student_name, id: latestEvent.student_id });
      
      setTimeout(() => setRecognitionState('idle'), 4000);
    }
  }, [latestEvent]);
};
```

---

### Task 8.3 — Replace Hardcoded Stats with Live Data

```javascript
import { getDailySummary } from '../services/api';
import { extractData } from '../services/apiHelpers';

const [attendanceStats, setAttendanceStats] = useState({ present: 0, total: 0 });

useEffect(() => {
  const fetchStats = async () => {
    try {
      const response = await getDailySummary();
      const data = extractData(response);
      setAttendanceStats({
        present: data.present_count || 0,
        total: data.total_students || 0,
        percentage: data.attendance_percentage || 0,
      });
    } catch (err) {
      console.error('Stats fetch error:', err);
    }
  };
  
  fetchStats();
  const interval = setInterval(fetchStats, 15000);
  return () => clearInterval(interval);
}, []);

// In JSX:
<span>{attendanceStats.present}</span>   // Instead of hardcoded 42
<span>{attendanceStats.percentage}%</span> // Instead of hardcoded 94%
```

---

### Task 8.4 — Add AI Module Status Indicator

Show whether the AI Module process is running (by checking if recent WebSocket events are flowing):

```javascript
const [aiModuleOnline, setAiModuleOnline] = useState(false);

useEffect(() => {
  // If we received a WebSocket event in the last 60 seconds, AI Module is active
  if (latestEvent) {
    setAiModuleOnline(true);
    const timeout = setTimeout(() => setAiModuleOnline(false), 60000);
    return () => clearTimeout(timeout);
  }
}, [latestEvent]);

// Status indicator in header
<span className={`w-2.5 h-2.5 rounded-full ${aiModuleOnline ? 'bg-green-500 animate-pulse' : 'bg-yellow-500'}`}></span>
<span>{aiModuleOnline ? 'AI Active' : 'AI Standby'}</span>
```

---

### Task 8.5 — Add Backend Health Check

Add a connection status indicator that checks if the Backend is reachable:

```javascript
import { getHealthStatus } from '../services/api';

const [backendOnline, setBackendOnline] = useState(false);

useEffect(() => {
  const checkHealth = async () => {
    try {
      await getHealthStatus();
      setBackendOnline(true);
    } catch {
      setBackendOnline(false);
    }
  };
  
  checkHealth();
  const interval = setInterval(checkHealth, 10000);
  return () => clearInterval(interval);
}, []);
```

---

### Task 8.6 — Update StatusPanel with Real Data

**File**: `src/components/attendance/StatusPanel.jsx`

Update to show real recognition results from WebSocket:

```javascript
const StatusPanel = ({ state, student, latestEvent }) => {
  // Show latest recognition result from WebSocket
  if (latestEvent) {
    return (
      <Card>
        <div className="text-green-400">
          <h3>{latestEvent.student_name}</h3>
          <p>Confidence: {latestEvent.confidence?.toFixed(1)}%</p>
          <p>Status: {latestEvent.status}</p>
        </div>
      </Card>
    );
  }
  
  // Default idle state
  return <Card><p>Waiting for recognition...</p></Card>;
};
```

---

## 🔄 Presentation Setup

During the live demo:
1. **Screen 1 (AI Module)**: Run `python recognize_faces.py` — shows OpenCV window with face detection overlays
2. **Screen 2 (Frontend)**: Open browser at `http://localhost:5173/attendance` — shows real-time logs and stats
3. As AI Module recognizes students, both screens update simultaneously

---

## ✅ Verification Checklist
- [ ] Simulation buttons removed
- [ ] WebSocket events display in activity feed
- [ ] Stats update from Backend API
- [ ] AI Module status indicator works
- [ ] Backend health check indicator works
- [ ] StatusPanel shows real recognition results
- [ ] System works during live demo with AI Module running separately

---

## 📁 Files Changed
| File | Action |
|---|---|
| `src/pages/Attendance.jsx` | **MODIFY** — remove simulation, add real-time |
| `src/components/attendance/StatusPanel.jsx` | **MODIFY** — show real data |
| `src/components/attendance/ActivityFeed.jsx` | **MODIFY** — connect to WebSocket |
