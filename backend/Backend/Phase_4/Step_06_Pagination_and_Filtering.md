# Step 06 – Pagination & Filtering

## Goal
Define a reusable pagination utility and flexible filtering parameters for the student list endpoint.

## Pagination Design
- Query params: `page: int = 1`, `page_size: int = 20` (max 100).
- Return response structure:
  ```json
  {
    "items": [...],
    "total": 123,
    "page": 1,
    "page_size": 20,
    "pages": 7
  }
  ```
- Use SQL `limit`/`offset`.

## Filtering
- Optional query parameters: `search: str`, `department: str`, `year: int`.
- Build a dynamic SQLAlchemy filter list.

## Implementation Steps
1. Create `app/utils/pagination.py` with a helper function `paginate(query, page, page_size)` returning `(items, total)`.
2. Add `apply_student_filters(query, params)` that adds `ilike` conditions for `search` and exact matches for `department`/`year`.
3. Update `StudentService.get_students` to call these utilities.

## Tests
- Verify default pagination returns first 20.
- Verify `page_size` cap.
- Verify filtering works with partial name matches.

---
*This file outlines the design; actual code will be added in later steps.*
