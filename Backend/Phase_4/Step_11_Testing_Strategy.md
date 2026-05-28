# Step 11 – Testing Strategy

## Goal
Define a comprehensive testing plan for the Student Management APIs, covering unit, integration, and end‑to‑end tests.

## Test Types
- **Unit Tests** – Service layer functions (create, read, update, delete) using a mocked SQLAlchemy session.
- **Integration Tests** – FastAPI `TestClient` against the live router, using a temporary test database (SQLite in‑memory).
- **E2E Tests** – Optional coverage with a Docker‑compose stack if the full stack (frontend + FastAPI + MySQL) is spun up.

## Files to create
- `app/tests/test_student_service.py`
- `app/tests/test_student_routes.py`

## Fixtures
- `client` fixture for `TestClient`.
- `async_session` fixture for a transactional DB session that rolls back after each test.

## Example Assertions
```python
response = client.post("/api/v1/students", json=payload)
assert response.status_code == 201
assert response.json()["email"] == payload["email"]
```

## Coverage Goal
- ≥ 90 % line coverage for `services/student_service.py` and `routes/students.py`.

## CI Integration
- Add pytest command to `GitHub Actions` workflow:
```yaml
- name: Run tests
  run: pytest -vv --cov=app
```

---
