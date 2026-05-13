# Step 08 — Middleware & Health Check Route

## 🎯 Objective
Create request logging middleware and a health check API endpoint for system monitoring.

---

## 📝 Tasks

### 1. Create Request Logging Middleware

Location: `app/middleware/__init__.py` or dedicated file.

**What it does:**
- Logs every incoming request: method, path, response time
- Example log: `INFO | GET /api/v1/health | 200 | 12ms`
- Helps identify slow endpoints and debug request flow

**How FastAPI middleware works:**
```python
@app.middleware("http")
async def log_requests(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = (time.time() - start_time) * 1000
    logger.info(f"{request.method} {request.url.path} | {response.status_code} | {duration:.1f}ms")
    return response
```

### 2. Create Health Check Route

Location: `app/routes/health.py`

**Endpoint:** `GET /api/v1/health`

**Response:**
```json
{
    "success": true,
    "message": "System is healthy",
    "data": {
        "server": "running",
        "database": "connected",
        "uptime": "2h 15m",
        "version": "1.0.0"
    }
}
```

**Why a health check?**
- **Monitoring**: Tools like Docker, Kubernetes, or simple cron jobs can ping this endpoint.
- **Debugging**: Quick way to verify server + DB are both up.
- **Frontend**: React app can call this on load to check backend availability.

### 3. Register Health Router in `app/routes/__init__.py`

Aggregate all routers into a single `api_router`:

```python
from fastapi import APIRouter
from app.routes.health import router as health_router

api_router = APIRouter()
api_router.include_router(health_router, prefix="/health", tags=["Health"])
```

This pattern scales cleanly — future routes just add one line each.

---

## 🧠 Key Decisions

| Decision | Rationale |
|----------|-----------|
| Middleware for logging (not per-route) | Catches ALL requests including 404s |
| Health check includes DB status | Single endpoint tells you if the whole system is up |
| Tags in router | Swagger UI groups endpoints by tag for clarity |
| Router aggregation in `__init__.py` | `main.py` only imports one router, stays clean |

---

## ✅ Checklist
- [ ] Request logging middleware created and registered
- [ ] Health check route created at `/api/v1/health`
- [ ] Health check tests DB connectivity
- [ ] Router aggregation set up in `routes/__init__.py`
- [ ] Swagger UI shows health endpoint under "Health" tag
