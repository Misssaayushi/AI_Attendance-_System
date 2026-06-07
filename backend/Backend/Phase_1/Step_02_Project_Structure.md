# Step 02 — Project Structure Creation

## 🎯 Objective

Create the complete backend folder structure with all necessary directories and `__init__.py` files to establish a clean, modular Python package architecture.

---

## 📌 Why This Step Matters?

A well-defined folder structure is the **backbone** of maintainable software. Every file has a clear home, every module has a single responsibility, and new developers can navigate the project intuitively.

Without `__init__.py` files, Python won't recognize directories as importable packages — leading to `ModuleNotFoundError` at runtime.

---

## 📝 Tasks

### 1. Create the `app/` Package and Sub-packages

Create the following directory tree inside `Backend/`:

```
backend/
│
├── app/
│   ├── __init__.py
│   ├── main.py              (created in Step 04)
│   ├── config.py            (created in Step 03)
│   │
│   ├── routes/
│   │   └── __init__.py
│   │
│   ├── database/
│   │   └── __init__.py
│   │
│   ├── models/
│   │   └── __init__.py
│   │
│   ├── services/
│   │   └── __init__.py
│   │
│   ├── scheduler/
│   │   └── __init__.py
│   │
│   ├── exports/
│   │   └── __init__.py
│   │
│   ├── utils/
│   │   └── __init__.py
│   │
│   ├── middleware/
│   │   └── __init__.py
│   │
│   └── tests/
│       └── __init__.py
│
├── logs/
└── run.py                   (created in Step 04)
```

### 2. Create All Directories

```bash
mkdir -p app/routes app/database app/models app/services app/scheduler app/exports app/utils app/middleware app/tests logs
```

> **Note (Windows):** Use `mkdir` for each directory individually, or use the Python script approach described below.

### 3. Create `__init__.py` Files

Every subdirectory under `app/` needs an `__init__.py` to be recognized as a Python package.

**`app/__init__.py`:**
```python
# AI Attendance System - Backend Application Package
```

**All other `__init__.py` files** (routes, database, models, etc.):
```python
# Package initialization
```

### 4. Create `logs/` Directory

The `logs/` directory stores runtime and error log files. Create it empty with a `.gitkeep` file:

```bash
mkdir logs
echo. > logs/.gitkeep
```

---

## 📁 Module Responsibility Map

| Directory | Responsibility | Created In |
|-----------|---------------|------------|
| `app/` | Root Python package | Step 02 |
| `app/routes/` | API endpoint definitions (thin controllers) | Step 08 |
| `app/database/` | DB engine, session factory, base model | Step 05 |
| `app/models/` | SQLAlchemy table definitions | Future Phase |
| `app/services/` | Business logic (attendance, reports) | Future Phase |
| `app/scheduler/` | APScheduler automated tasks | Future Phase |
| `app/exports/` | Excel/PDF file generation | Future Phase |
| `app/utils/` | Logger, response formatter, helpers | Step 07 |
| `app/middleware/` | Error handlers, request middleware | Step 06 |
| `app/tests/` | Unit and integration tests | Step 09 |
| `logs/` | Log file storage | Step 02 |

---

## 🧠 Design Decision: Why Separate `routes/` and `services/`?

**Anti-pattern (monolithic routes):**
```python
@router.post("/mark-attendance")
async def mark_attendance(data: AttendanceRequest, db: Session):
    # 50+ lines of business logic directly in the route
    student = db.query(Student).filter(...)
    if not student: raise HTTPException(...)
    attendance = Attendance(...)
    db.add(attendance)
    # ... more logic
```

**Our pattern (thin routes + service layer):**
```python
# routes/attendance.py
@router.post("/mark-attendance")
async def mark_attendance(data: AttendanceRequest, db: Session):
    return attendance_service.mark(data, db)  # 1 line

# services/attendance_service.py
def mark(data, db):
    # All business logic here — easy to test independently
```

This separation means:
- Routes are **testable without a database**.
- Services are **reusable across multiple routes**.
- Business logic changes don't touch the HTTP layer.

---

## ✅ Completion Checklist

- [ ] `app/` directory created with `__init__.py`
- [ ] All 9 sub-packages created with `__init__.py` files
- [ ] `logs/` directory created with `.gitkeep`
- [ ] All imports work (`from app.routes import ...` doesn't error)
- [ ] No extra unnecessary files in the structure
