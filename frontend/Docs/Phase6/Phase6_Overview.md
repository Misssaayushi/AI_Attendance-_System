# Phase 6: Attendance Records Page — Implementation Plan

## 1. Records Page Architecture Strategy
- **Unified Layout**: Maintain the responsive admin layout structure wrapped by `MainLayout` (sidebar + header).
- **Control Bar**: A unified command center at the top for actions (select date range, export logs).
- **Interactive Filtering Bar**: A dedicated filtering panel with multi-parameter controls (search, department filter, status filter).
- **Responsive Data Grid**: A responsive grid containing the main records table and pagination controls.
- **Detail Modal/Drawer**: A sliding detail drawer or overlay modal to inspect a specific student's attendance history and biometric confidence telemetry.

---

## 2. Advanced Filtering and Search Engine
- **Multi-parameter Search**: Allow users to query by Student Name, Roll Number, or Department.
- **Dynamic Filters**:
  - **Department**: CS, IT, ME, EE, or "All".
  - **Attendance Status**: Present, Absent, Late, or "All".
  - **Date Selector**: Allow filtering records by a selected calendar date.
- **Live Filtering**: Apply search queries and filters immediately via React state updates.

---

## 3. Component Breakdown
- `Records`: Main parent page component that holds the global state, filter configurations, and triggers actions.
- `RecordsFilterBar`: Interactive filtering input controls (comboboxes for departments and status, text search input).
- `RecordsTable`: Styled grid to show student rows, status badges, check-in timestamps, and action buttons.
- `RecordsPagination`: Bottom bar managing page numbers, records-per-page selectors, and record count indicators.
- `RecordDetailModal`: Dialog overlay showcasing a student's full historical attendance rates, check-in timelines, and confidence scores.

---

## 4. Sorting & Formatting Strategy
- **Multi-column Sorting**: Users can sort records by Student Name, Roll Number, Time, or Status.
- **Time/Date Formatter**: Helper utilities to format timestamps and dates cleanly (e.g., `YYYY-MM-DD` and `hh:mm AM/PM`).
- **Dynamic Status Badges**:
  - `Present`: Neon green backdrop/text.
  - `Late`: Cyber orange/amber backdrop/text.
  - `Absent`: Crimson red backdrop/text.

---

## 5. CSV/Excel Export Pipeline
- **Client-side Export**: Process the currently filtered datasets and generate a standard downloadable CSV file.
- **Universal Comma Delimiter**: Ensure spreadsheet compatibility (Excel, Google Sheets).
- **Auto-naming convention**: Format generated files as `attendance_records_[Date].csv` for clean file management.

---

## 6. State / Data Flow Planning
- **Centralized Page State**:
  - `records`: Complete array of historical attendance logs.
  - `filters`: Search queries, status selections, and department selections.
  - `sortConfig`: Active sorting column and direction (ascending/descending).
  - `currentPage` & `itemsPerPage` for pagination.
- **Mock Data Layer**: Rich set of realistic attendance history records (50+ entries) representing multiple departments and statuses.

---

## 7. Responsive Records Layout
- **Mobile Cards**: Table headers collapse on small screens into individual student activity cards.
- **Horizontal Scrolling**: Enable horizontal container scrolls for medium screens to prevent layout breaking.
- **Responsive Header Layout**: Stack action items (select date, export) vertically on mobile and horizontally on desktop.

---

## 8. Future Backend Integration Strategy
- Map state properties directly to URL query parameters (`?dept=CS&status=Present&search=Rahul`).
- Prepare Axios fetch template function `getAttendanceRecords(filters)` designed to call the FastAPI backend `/api/records` endpoint.

---

## 9. Performance Optimization Approach
- **Memoized Filtering**: Wrap search and sorting logic in React `useMemo` hooks to avoid heavy calculations on every keystroke.
- **Virtualized Lists (Optional)**: If data scales past 1000+ entries, establish virtual rendering to only display visible rows.

---

## 10. Implementation Roadmap
- **Step 1**: Establish advanced mockup data array in `Records.jsx` (50+ entries).
- **Step 2**: Rebuild the Filters Bar to connect selection states dynamically.
- **Step 3**: Rebuild the Table layout with full multi-column sorting and badge controls.
- **Step 4**: Code the frontend CSV export utility.
- **Step 5**: Code the detail inspector popup modal component.
- **Step 6**: Run builds and finalize responsive polish.
