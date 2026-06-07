# Step 06 — Error Handling Architecture

## 🎯 Objective
Create a centralized, reusable error handling system with global exception handlers and custom exception classes.

---

## 📌 Why Centralized Error Handling?

Without it, every route duplicates try/catch blocks. With it:
- **Consistent JSON error responses** across all endpoints.
- **One place** to update error format.
- **Graceful failures** — server never returns raw tracebacks to clients.

---

## 📝 Tasks

### 1. Create `app/middleware/error_handler.py`

**Custom Exception Classes:**

| Exception | HTTP Code | Use Case |
|-----------|-----------|----------|
| `AppException` | Base class | Parent for all custom exceptions |
| `NotFoundException` | 404 | Resource not found |
| `BadRequestException` | 400 | Invalid input data |
| `DatabaseException` | 500 | DB connection/query failures |
| `UnauthorizedException` | 401 | Auth failures (future) |
| `ValidationException` | 422 | Data validation errors |

**Global Exception Handlers:**

```python
# Catches our custom exceptions → clean JSON
@app.exception_handler(AppException)

# Catches FastAPI validation errors → formatted JSON
@app.exception_handler(RequestValidationError)

# Catches everything else → generic 500 JSON
@app.exception_handler(Exception)
```

**Standard Error Response Format:**

```json
{
    "success": false,
    "status_code": 404,
    "message": "Student not found",
    "error_type": "NotFoundException",
    "timestamp": "2026-05-12T23:00:00"
}
```

### 2. Register Handlers in `main.py`

A `register_error_handlers(app)` function will be called inside `create_app()`.

---

## 🧠 Key Decisions

| Decision | Rationale |
|----------|-----------|
| Custom exception hierarchy | Type-safe errors, IDE autocomplete, easy to catch specific types |
| Global handlers over try/catch | DRY — one place for all error formatting |
| Timestamp in error response | Helps correlate errors with logs during debugging |
| Never expose stack traces | Security — raw tracebacks reveal internal architecture |

---

## ✅ Checklist
- [ ] Custom exception classes created (AppException, NotFoundException, etc.)
- [ ] Global exception handlers registered
- [ ] All errors return consistent JSON format
- [ ] Unhandled exceptions return generic 500 (no stack trace)
- [ ] Handlers integrated into `main.py` via `register_error_handlers()`
