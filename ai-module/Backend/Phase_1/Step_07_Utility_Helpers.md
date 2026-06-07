# Step 07 — Utility Helpers

## 🎯 Objective
Create reusable utility modules for structured logging and standardized API response formatting.

---

## 📝 Tasks

### 1. Create `app/utils/logger.py`

A structured logging system that writes to both **console** and **log file**.

**Features:**
- Timestamped log entries with module name
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Console output (colored for readability in terminal)
- File output to `logs/app.log` (for production debugging)
- Rotating file handler to prevent log files from growing infinitely

**Usage across the project:**
```python
from app.utils.logger import logger

logger.info("Server started successfully")
logger.error(f"Database connection failed: {error}")
logger.debug(f"Query returned {count} results")
```

### 2. Create `app/utils/response.py`

Standardized JSON response helpers for consistent API output.

**Success Response Format:**
```json
{
    "success": true,
    "status_code": 200,
    "message": "Students fetched successfully",
    "data": [...],
    "timestamp": "2026-05-12T23:00:00"
}
```

**Helper Functions:**
- `success_response(data, message, status_code)` → Standard success JSON
- `error_response(message, status_code, error_type)` → Standard error JSON
- `paginated_response(data, page, per_page, total)` → Paginated list JSON (future)

**Why standardized responses?**
- Frontend team always knows the exact response structure.
- No guessing whether data is in `response.data` or `response.results`.
- Error handling is uniform across all endpoints.

---

## 🧠 Key Decisions

| Decision | Rationale |
|----------|-----------|
| Python `logging` module (not print) | Supports levels, file output, rotation, formatting |
| Rotating file handler | Log files auto-archive at 5MB, keeps last 5 files |
| Response helpers as functions | Lightweight, no class overhead, easy to import |
| Timestamp in every response | Frontend can display "last updated" timestamps |

---

## ✅ Checklist
- [ ] `logger.py` with console + file handlers
- [ ] `response.py` with `success_response()` and `error_response()`
- [ ] Log file created at `logs/app.log` on first use
- [ ] Logger is importable from any module
- [ ] Response format is consistent across all helpers
