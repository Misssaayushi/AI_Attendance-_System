# Step 05 – Route Registration

This file documents how to register the `students` router with the main FastAPI application.

```python
# app/main.py (excerpt)
from fastapi import FastAPI
from app.routes import students

app = FastAPI()
app.include_router(students.router, prefix="/api/v1")
```

**Key points**
- Register after all middleware (CORS, auth) is added.
- Use a dedicated `api/v1` prefix for versioning.
- Keep the registration snippet in a separate module (`app/routes/__init__.py`) for clean imports.
```
