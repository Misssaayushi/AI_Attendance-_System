# Step 09 – Response Utilities

## Goal
Create helper functions to standardize JSON responses across the Student Management API.

## Files to create
- `app/utils/response.py`

## Functions
- `success(data: Any, message: str = "OK") -> JSONResponse` – wraps payload with `{ "status": "success", "message": message, "data": data }`.
- `error(detail: str, status_code: int = 400) -> JSONResponse` – returns `{ "status": "error", "detail": detail }`.

## Usage
Import these helpers in routers and services to return uniform responses.
