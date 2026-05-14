# Step 04 — FastAPI Server Setup

## 🎯 Objective

Create the FastAPI application with app factory pattern, CORS configuration, modular router registration, and a clean entry point (`run.py`).

---

## 📌 Why App Factory Pattern?

Instead of creating the FastAPI app as a global variable, we use a **`create_app()` function**:

```python
# ❌ Anti-pattern: Global app
app = FastAPI()

# ✅ Our pattern: Factory function
def create_app() -> FastAPI:
    app = FastAPI(...)
    configure_cors(app)
    register_routes(app)
    register_error_handlers(app)
    return app
```

**Benefits:**
- **Testing**: Create fresh app instances for each test — no state leakage.
- **Configuration**: Pass different settings for dev/test/prod.
- **Clarity**: Startup sequence is explicit and readable.

---

## 📝 Tasks

### 1. Create `app/main.py`

The heart of the backend. This file:

1. **Creates the FastAPI instance** with metadata (title, description, version).
2. **Configures CORS** to allow the React frontend to communicate.
3. **Registers routers** from `routes/` package.
4. **Registers error handlers** from `middleware/`.
5. **Adds startup/shutdown events** for logging and DB connection lifecycle.

**FastAPI Instance Configuration:**

```python
FastAPI(
    title="AI Attendance System API",
    description="Backend API for AI-Based Smart Attendance Management System",
    version="1.0.0",
    docs_url="/docs",        # Swagger UI
    redoc_url="/redoc",      # ReDoc
    debug=settings.DEBUG_MODE
)
```

### 2. Configure CORS Middleware

**What is CORS?**

Cross-Origin Resource Sharing — the browser's security mechanism that blocks frontend (React on `localhost:3000`) from calling backend (FastAPI on `localhost:8000`) unless explicitly allowed.

**Configuration:**

```python
CORSMiddleware(
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],        # GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],        # Authorization, Content-Type, etc.
)
```

**Why these origins?**
- `localhost:3000` — Create React App default
- `localhost:5173` — Vite (modern React) default

### 3. Register Modular Routers

All routes are aggregated in `routes/__init__.py` and mounted with a single `include_router()` call:

```python
from app.routes import api_router

app.include_router(api_router, prefix=settings.API_PREFIX)
```

This means all routes will be prefixed with `/api/v1/` — enabling API versioning.

### 4. Add Startup & Shutdown Events

```python
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 AI Attendance System Backend starting...")
    # Future: verify DB connection, initialize scheduler

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 Backend shutting down...")
    # Future: close DB connections, stop scheduler
```

### 5. Create `run.py` (Entry Point)

Location: `Backend/run.py`

A simple script that imports the app and runs Uvicorn:

```python
import uvicorn
from app.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.DEBUG_MODE  # Auto-reload on code changes
    )
```

**Why `run.py` at root level?**
- Clean separation: `app/` is the package, `run.py` is the launcher.
- Easy to run: `python run.py` from `Backend/` directory.
- `reload=True` in debug mode means code changes auto-restart the server.

### 6. Create Root Endpoint

A simple root `/` endpoint for basic server verification:

```python
@app.get("/")
async def root():
    return {
        "system": "AI Attendance System",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs"
    }
```

---

## 🧠 Design Decision: Why `/api/v1/` Prefix?

API versioning from Day 1 means:

- **v1 routes** live at `/api/v1/attendance`, `/api/v1/students`
- **v2 routes** (future) live at `/api/v2/...` without breaking v1 clients
- Frontend only needs to update the base URL to migrate

---

## 🔄 Request Flow

```
Client Request
    ↓
CORS Middleware (validates origin)
    ↓
Error Handler Middleware (catches exceptions)
    ↓
Router Matching (/api/v1/...)
    ↓
Route Handler (in routes/)
    ↓
Service Layer (in services/)
    ↓
Database (via SQLAlchemy)
    ↓
JSON Response → Client
```

---

## ✅ Completion Checklist

- [ ] `app/main.py` created with `create_app()` factory
- [ ] CORS middleware configured for React frontend
- [ ] Router registration system in place
- [ ] Startup and shutdown event handlers added
- [ ] Root `/` endpoint returns system info
- [ ] `run.py` created at project root
- [ ] Server starts successfully with `python run.py`
- [ ] Swagger docs accessible at `http://localhost:8000/docs`
