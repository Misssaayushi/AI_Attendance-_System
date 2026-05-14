# Step 09 — Testing Workflow

## 🎯 Objective
Create test scripts to validate the entire Phase 1 setup: server startup, database connectivity, configuration loading, route initialization, and CORS.

---

## 📝 Tasks

### 1. Create `app/tests/test_setup.py`

**Test Cases:**

| # | Test | What It Validates |
|---|------|-------------------|
| 1 | `test_server_startup` | FastAPI app creates without errors |
| 2 | `test_root_endpoint` | `GET /` returns system info JSON |
| 3 | `test_health_endpoint` | `GET /api/v1/health` returns health status |
| 4 | `test_database_connection` | MySQL is reachable via `test_db_connection()` |
| 5 | `test_config_loading` | All settings load from `.env` correctly |
| 6 | `test_cors_headers` | Response includes correct CORS headers |
| 7 | `test_404_handling` | Unknown routes return JSON (not HTML error page) |
| 8 | `test_docs_endpoint` | Swagger UI at `/docs` returns 200 |

**Testing Tool:** FastAPI's built-in `TestClient` (uses `httpx` under the hood).

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "running"
```

### 2. How to Run Tests

```bash
# From Backend/ directory with venv activated
python -m pytest app/tests/ -v
```

Or without pytest (simple script):
```bash
python app/tests/test_setup.py
```

---

## 🧠 Key Decisions

| Decision | Rationale |
|----------|-----------|
| `TestClient` (not real server) | No need to start uvicorn — tests run instantly |
| Both pytest and standalone | Pytest for CI, standalone for quick manual checks |
| Test CORS separately | Common source of frontend integration bugs |
| Test 404 returns JSON | Default FastAPI 404 is HTML — we override to JSON |

---

## ✅ Checklist
- [ ] `test_setup.py` created with all 8 test cases
- [ ] All tests pass with `python -m pytest app/tests/ -v`
- [ ] Tests can also run standalone with `python app/tests/test_setup.py`
- [ ] CORS test validates correct `Access-Control-Allow-Origin` header
