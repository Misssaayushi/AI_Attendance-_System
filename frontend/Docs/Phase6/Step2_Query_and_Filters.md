# Step 2: Query & Interactive Filters

## Goal
Implement a responsive filters panel that binds search input, department selectors, status dropdowns, and date calendars to state hooks for live dataset filtering.

## Tasks
- [x] Integrate React state hooks in `Records.jsx` for:
  - `searchQuery` (filters by name/ID)
  - `selectedDept` (filters by branch)
  - `selectedStatus` (filters by check-in result)
  - `selectedDate` (filters by specific date)
- [x] Wrap filter criteria logic inside a `useMemo` calculation block to recalculate only when query state changes.
- [x] Implement a "Clear Filters" utility button that resets all states back to default values.

## Files Affected
- `src/pages/Records.jsx`
