# Step 6: Records Page Backend Integration

## 🎯 Objective
Replace the `mockAttendanceRecords` hardcoded array in `Records.jsx` with real attendance data from the Backend API, including server-side pagination, filtering, and sorting.

---

## 📊 Current State

### Records.jsx (❌ Mock Data)
- Uses `mockAttendanceRecords` — a hardcoded array of 20 fake records
- Client-side filtering, sorting, and pagination on this static array
- CSV export works on mock data only
- No connection to Backend

### Backend Attendance API (✅ Ready)
```
GET /api/v1/attendance/?page=1&page_size=20&student_id=1&department=CS&status=Present&from_date=2026-05-01&to_date=2026-05-31&search=rahul
```

Returns:
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "student_id": 42,
        "student_name": "Rahul Sharma",
        "roll_number": "STU-2026-042",
        "attendance_date": "2026-05-20",
        "attendance_time": "09:01:00",
        "status": "Present",
        "confidence_score": null,
        "source": null,
        "created_at": null
      }
    ],
    "total": 150,
    "page": 1,
    "page_size": 20,
    "pages": 8
  }
}
```

---

## 📝 Implementation Tasks

### Task 6.1 — Replace Mock Data with API Calls

Remove `mockAttendanceRecords` and fetch real data:

```javascript
import { listAttendance } from '../services/api';
import { extractData, extractErrorMessage } from '../services/apiHelpers';

const Records = () => {
  const [records, setRecords] = useState([]);
  const [totalRecords, setTotalRecords] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDept, setSelectedDept] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('');
  const [selectedDate, setSelectedDate] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 20;

  // Fetch data whenever filters or page changes
  useEffect(() => {
    fetchRecords();
  }, [currentPage, searchQuery, selectedDept, selectedStatus, selectedDate]);

  const fetchRecords = async () => {
    try {
      setIsLoading(true);
      const params = {
        page: currentPage,
        page_size: pageSize,
      };
      
      if (searchQuery) params.search = searchQuery;
      if (selectedDept) params.department = selectedDept;
      if (selectedStatus) params.status = selectedStatus;
      if (selectedDate) {
        params.from_date = selectedDate;
        params.to_date = selectedDate;
      }

      const response = await listAttendance(params);
      const data = extractData(response);
      
      setRecords(data.items || []);
      setTotalRecords(data.total || 0);
      setTotalPages(data.pages || 1);
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };
  
  // ... rest of component
};
```

---

### Task 6.2 — Use Server-Side Pagination

Remove client-side pagination logic. The Backend already paginates:

```diff
-const itemsPerPage = 8;
-const totalPages = Math.ceil(filteredAndSortedRecords.length / itemsPerPage) || 1;
-const startIndex = (currentPage - 1) * itemsPerPage;
-const paginatedRecords = filteredAndSortedRecords.slice(startIndex, startIndex + itemsPerPage);

+// totalPages and records come directly from API response
+// currentPage changes trigger new API call via useEffect
```

---

### Task 6.3 — Debounce Search Input

Add a debounce to prevent excessive API calls while typing:

```javascript
import { useState, useEffect, useCallback } from 'react';

const useDebounce = (value, delay = 500) => {
  const [debouncedValue, setDebouncedValue] = useState(value);
  useEffect(() => {
    const handler = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(handler);
  }, [value, delay]);
  return debouncedValue;
};

// In Records component:
const [rawSearch, setRawSearch] = useState('');
const debouncedSearch = useDebounce(rawSearch, 400);

useEffect(() => {
  setSearchQuery(debouncedSearch);
  setCurrentPage(1);
}, [debouncedSearch]);
```

---

### Task 6.4 — Map Backend Response to Table Columns

Backend returns different field names than the mock data:

| Mock Data Field | Backend Field | Mapping |
|---|---|---|
| `record.id` | `record.roll_number` | Use `roll_number` for display ID |
| `record.name` | `record.student_name` | Direct |
| `record.date` | `record.attendance_date` | Direct |
| `record.time` | `record.attendance_time` | Format `HH:MM:SS` → `HH:MM AM/PM` |
| `record.department` | *Not in response* | Need to join from student data |
| `record.status` | `record.status` | Direct |

**Fix time formatting**:
```javascript
const formatTime = (timeStr) => {
  if (!timeStr || timeStr === '---') return '---';
  const [h, m] = timeStr.split(':');
  const hour = parseInt(h);
  const ampm = hour >= 12 ? 'PM' : 'AM';
  const displayHour = hour % 12 || 12;
  return `${displayHour}:${m} ${ampm}`;
};
```

---

### Task 6.5 — Connect Export to Backend Export API

Replace client-side CSV generation with Backend export:

```javascript
import { getExportPreview } from '../services/api';

const handleExportCSV = async () => {
  try {
    const params = {};
    if (selectedDate) {
      params.from_date = selectedDate;
      params.to_date = selectedDate;
    }
    
    const response = await getExportPreview(params);
    const data = extractData(response);
    
    // Convert Backend export rows to CSV
    const rows = data.rows || [];
    if (rows.length === 0) {
      alert("No data available to export.");
      return;
    }
    
    const headers = Object.keys(rows[0]);
    const csvContent = "data:text/csv;charset=utf-8,"
      + [headers.join(','), ...rows.map(r => headers.map(h => `"${r[h] ?? ''}"`).join(','))].join('\n');
    
    const link = document.createElement("a");
    link.href = encodeURI(csvContent);
    link.download = `attendance_records_${selectedDate || 'all'}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  } catch (err) {
    alert("Export failed: " + extractErrorMessage(err));
  }
};
```

---

### Task 6.6 — Add Loading Table Skeleton

```jsx
{isLoading ? (
  <tbody>
    {[...Array(pageSize)].map((_, i) => (
      <tr key={i}>
        <td colSpan="5" className="px-6 py-4">
          <div className="h-4 bg-gray-800 rounded animate-pulse" />
        </td>
      </tr>
    ))}
  </tbody>
) : (
  // ... existing table body
)}
```

---

## ✅ Verification Checklist
- [ ] Records page loads real data from `GET /api/v1/attendance/`
- [ ] Server-side pagination works (page navigation fetches new data)
- [ ] Search filter works (debounced, server-side)
- [ ] Department filter works
- [ ] Status filter works (Present/Absent/Late)
- [ ] Date filter works
- [ ] Export CSV uses Backend export preview data
- [ ] Loading skeletons display during fetch
- [ ] Error state displays on API failure

---

## 📁 Files Changed
| File | Action |
|---|---|
| `src/pages/Records.jsx` | **MODIFY** — replace mock data with API calls |
| `src/services/api.js` | Already updated in Step 2 |
