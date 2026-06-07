# Step 08 – Error Handling

## Goal
Define a consistent error hierarchy and FastAPI exception handlers for the Student Management APIs.

## Files to create
- `app/exceptions.py`

## Exception Classes
- `AppException` – base class with `status_code` and `detail`.
- `StudentNotFoundException`
- `DuplicateRollNumberException`
- `InvalidFaceEncodingException`

## FastAPI Handlers
Add a handler in `app/main.py` (or a dedicated `error_handlers.py`) that catches `AppException` and returns a JSON response:
```python
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
```

## Usage
Service layer raises these exceptions; router does not need try/except blocks.

---
