# Step 3: Charts & Analytics (Chart.js)

## Goal
Integrate visual analysis tools plotting daily, monthly, and departmental attendance trends through Chart.js wrappers.

## Tasks
* [ ] Integrate Chart.js dependencies via `react-chartjs-2`.
* [ ] Code the `AttendanceCharts` container in `src/components/dashboard/AttendanceCharts.jsx`.
* [ ] Construct the 3 mandatory charts using mock data models:
  1. **Weekly Attendance Trend** (Line Chart): Displays attendance rates across standard weekdays (Mon-Fri).
  2. **Monthly Attendance Overview** (Bar Chart): Tracks comparison statistics across consecutive months.
  3. **Department-wise Attendance Distribution** (Doughnut Chart): Shows proportion distribution for branches (`CS`, `IT`, `ME`, `EE`).
* [ ] Style with customizable gradients, custom hover tooltips, and custom chart legends that align with a dark theme.

## Files Affected
* `src/components/dashboard/AttendanceCharts.jsx`
* `src/pages/Dashboard.jsx`
