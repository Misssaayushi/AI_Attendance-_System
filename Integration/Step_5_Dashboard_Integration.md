# Step 5: Dashboard Live Data Integration

## 🎯 Objective
Replace all hardcoded/mock stats in the Dashboard page with real data from the Backend's dashboard analytics APIs.

---

## 📊 Current State

### Dashboard.jsx (❌ Mock Data)
```javascript
const [stats, setStats] = useState({
  totalStudents: 150,        // ← Hardcoded
  presentToday: 128,         // ← Hardcoded
  absentToday: 22,           // ← Hardcoded
  attendancePercentage: '85.3%' // ← Hardcoded
});
```

Calls `getDashboardStats()` which hits non-existent `/api/v1/attendance/stats`. Falls back to hardcoded values silently.

### Backend Dashboard APIs (✅ Ready)
| Endpoint | Returns |
|---|---|
| `GET /api/v1/dashboard/summary` | `{ total_students, present_count, absent_count, late_count, attendance_percentage, ... }` |
| `GET /api/v1/dashboard/stats/daily` | Daily breakdown with department data |
| `GET /api/v1/dashboard/stats/department` | Per-department attendance stats |
| `GET /api/v1/dashboard/graphs/weekly` | Weekly trend data (labels + values) |
| `GET /api/v1/dashboard/graphs/monthly` | Monthly trend data |
| `GET /api/v1/dashboard/graphs/department` | Department comparison bar chart data |

---

## 📝 Implementation Tasks

### Task 5.1 — Rewrite Dashboard.jsx Data Fetching

```javascript
import { getDashboardSummary, getWeeklyTrend, getDepartmentStats } from '../services/api';
import { extractData } from '../services/apiHelpers';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setIsLoading(true);
        const response = await getDashboardSummary();
        const data = extractData(response);
        
        setStats({
          totalStudents: data.total_students || 0,
          presentToday: data.present_count || 0,
          absentToday: data.absent_count || 0,
          lateToday: data.late_count || 0,
          attendancePercentage: `${(data.attendance_percentage || 0).toFixed(1)}%`,
        });
      } catch (err) {
        setError('Failed to load dashboard data');
        console.error('Dashboard fetch error:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchDashboardData();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);
  
  // ... render with loading/error states
};
```

---

### Task 5.2 — Connect AttendanceCharts Component

**File**: `src/components/dashboard/AttendanceCharts.jsx`

This component renders Chart.js charts. Connect it to the Backend graph APIs:

```javascript
import { getWeeklyTrend, getMonthlyTrend, getDepartmentComparison } from '../../services/api';
import { extractData } from '../../services/apiHelpers';

// Fetch weekly trend data
const fetchWeeklyData = async () => {
  const response = await getWeeklyTrend();
  const data = extractData(response);
  
  // Backend returns: { labels: [...], present: [...], absent: [...], late: [...] }
  setChartData({
    labels: data.labels,
    datasets: [
      { label: 'Present', data: data.present, borderColor: '#22c55e', ... },
      { label: 'Absent', data: data.absent, borderColor: '#ef4444', ... },
      { label: 'Late', data: data.late, borderColor: '#f59e0b', ... },
    ]
  });
};
```

---

### Task 5.3 — Connect StudentTable Component

**File**: `src/components/dashboard/StudentTable.jsx`

Currently uses hardcoded student data. Replace with:

```javascript
import { listStudents } from '../../services/api';
import { extractData } from '../../services/apiHelpers';

const StudentTable = () => {
  const [students, setStudents] = useState([]);
  
  useEffect(() => {
    const fetchStudents = async () => {
      try {
        const response = await listStudents({ page: 1, page_size: 10 });
        const data = extractData(response);
        setStudents(data.items || []);
      } catch (err) {
        console.error('Failed to load students:', err);
      }
    };
    fetchStudents();
  }, []);
  
  // Map Backend response fields to table columns
  // Backend returns: { id, first_name, last_name, roll_number, department, ... }
};
```

---

### Task 5.4 — Connect ActivityFeed Component

**File**: `src/components/dashboard/ActivityFeed.jsx`

Currently shows hardcoded activities. Replace with recent attendance records:

```javascript
import { listAttendance } from '../../services/api';
import { extractData } from '../../services/apiHelpers';

const ActivityFeed = () => {
  const [activities, setActivities] = useState([]);
  
  useEffect(() => {
    const fetchRecentActivity = async () => {
      try {
        const today = new Date().toISOString().split('T')[0];
        const response = await listAttendance({ 
          page: 1, 
          page_size: 10, 
          from_date: today 
        });
        const data = extractData(response);
        setActivities(data.items || []);
      } catch (err) {
        console.error('Failed to load activity feed:', err);
      }
    };
    fetchRecentActivity();
    
    // Poll every 15 seconds for new activity
    const interval = setInterval(fetchRecentActivity, 15000);
    return () => clearInterval(interval);
  }, []);
};
```

---

### Task 5.5 — Add Loading & Error States

Add skeleton loading states and error boundaries to all dashboard components:

```jsx
// Loading skeleton for StatCard
if (isLoading) {
  return (
    <div className="grid grid-cols-4 gap-6">
      {[...Array(4)].map((_, i) => (
        <div key={i} className="h-24 bg-gray-800/50 rounded-2xl animate-pulse" />
      ))}
    </div>
  );
}

// Error state
if (error) {
  return (
    <div className="text-center py-12">
      <p className="text-red-400">{error}</p>
      <button onClick={fetchDashboardData} className="mt-4 text-blue-400">
        Retry
      </button>
    </div>
  );
}
```

---

## ✅ Verification Checklist
- [ ] StatCards show real data from `GET /api/v1/dashboard/summary`
- [ ] Charts render real trend data from Backend graph APIs
- [ ] StudentTable loads students from `GET /api/v1/students/`
- [ ] ActivityFeed shows today's attendance records
- [ ] Auto-refresh works (30-second interval)
- [ ] Loading skeletons display while data loads
- [ ] Error states display with retry button

---

## 📁 Files Changed
| File | Action |
|---|---|
| `src/pages/Dashboard.jsx` | **MODIFY** — replace mock stats with API calls |
| `src/components/dashboard/AttendanceCharts.jsx` | **MODIFY** — connect to graph APIs |
| `src/components/dashboard/StudentTable.jsx` | **MODIFY** — fetch real student data |
| `src/components/dashboard/ActivityFeed.jsx` | **MODIFY** — fetch recent attendance |
| `src/components/dashboard/StatCard.jsx` | **MODIFY** — add loading state |
