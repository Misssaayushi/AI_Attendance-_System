# Phase 1 — Backend Project Setup & Architecture

## 🎯 Phase Goal

Build the **foundation** of a scalable, production-grade FastAPI backend for the AI-Based Smart Attendance Management System. This phase focuses **exclusively** on infrastructure — no business logic, no APIs, no attendance features.

---

## 🏗️ Backend Architecture Strategy

### Why FastAPI?

- **Async-native**: Built on Starlette, supports `async/await` out of the box — critical for handling concurrent attendance requests.
- **Auto documentation**: Swagger UI (`/docs`) and ReDoc (`/redoc`) are generated automatically.
- **Type safety**: Pydantic models enforce request/response validation at the framework level.
- **Performance**: One of the fastest Python frameworks — benchmarks close to Node.js/Go.
- **Dependency injection**: Built-in DI system simplifies database sessions, auth, and config loading.

### Why SQLAlchemy ORM?

- **Database abstraction**: Switch between MySQL/PostgreSQL/SQLite without rewriting queries.
- **Session management**: Connection pooling and session lifecycle handled cleanly.
- **Migration support**: Pairs with Alembic for schema migrations in production.
- **Relationship mapping**: Complex joins (students ↔ attendance ↔ courses) map naturally to Python classes.

### Why Modular Architecture?

A monolithic `main.py` becomes unmaintainable after 500+ lines. Our architecture separates concerns:

| Layer | Responsibility |
|-------|---------------|
| `routes/` | HTTP endpoint definitions (thin controllers) |
| `services/` | Business logic (attendance marking, validation) |
| `models/` | Database table definitions (SQLAlchemy models) |
| `database/` | Connection management, session factories |
| `middleware/` | Cross-cutting concerns (CORS, error handling, logging) |
| `utils/` | Reusable helpers (response formatting, validators) |
| `exports/` | Excel/PDF generation (future) |
| `scheduler/` | Automated tasks via APScheduler (future) |
| `tests/` | Unit and integration tests |

---

## 📁 Folder Structure (Explained)

```
backend/
│
├── app/
│   ├── __init__.py          # Makes app a Python package
│   ├── main.py              # FastAPI app factory — creates and configures the app
│   ├── config.py            # Centralized settings loaded from .env
│   │
│   ├── routes/
│   │   ├── __init__.py      # Router aggregation — single import point
│   │   └── health.py        # Health check endpoint (/api/health)
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py    # SQLAlchemy engine + session factory
│   │   └── base.py          # Declarative base for all models
│   │
│   ├── models/
│   │   └── __init__.py      # Future: Student, Attendance, Course models
│   │
│   ├── services/
│   │   └── __init__.py      # Future: Business logic layer
│   │
│   ├── scheduler/
│   │   └── __init__.py      # Future: APScheduler tasks
│   │
│   ├── exports/
│   │   └── __init__.py      # Future: Excel/PDF generation
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── logger.py        # Structured logging configuration
│   │   └── response.py      # Standardized JSON response helpers
│   │
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── error_handler.py # Global exception handlers
│   │
│   └── tests/
│       ├── __init__.py
│       └── test_setup.py    # Startup, DB, config, CORS validation tests
│
├── logs/                    # Runtime log files (gitignored)
├── .env                     # Environment variables (gitignored)
├── .env.example             # Template for team members
├── requirements.txt         # Pinned Python dependencies
├── .gitignore               # Ignore venv, logs, .env, __pycache__
├── README.md                # Project documentation
└── run.py                   # Entry point — runs uvicorn server
```

### Key Architecture Decisions

1. **`app/` as a package**: Using `__init__.py` files makes imports clean (`from app.config import settings`).
2. **`run.py` at root**: Keeps the entry point separate from app logic. Easy to run with `python run.py`.
3. **`config.py` with Pydantic**: Environment variables are validated at startup — fail fast, not at runtime.
4. **`routes/__init__.py` as aggregator**: All routers register in one place, `main.py` only imports the master router.
5. **`database/connection.py`**: Single source of truth for DB sessions — every route gets a session via FastAPI's `Depends()`.

---

## 📋 Step Index

| Step | File | Description |
|------|------|-------------|
| 01 | `Step_01_Environment_Setup.md` | Python venv, pip installs, requirements.txt |
| 02 | `Step_02_Project_Structure.md` | Create all folders and `__init__.py` files |
| 03 | `Step_03_Environment_Configuration.md` | `.env`, `.env.example`, `config.py` |
| 04 | `Step_04_FastAPI_Server_Setup.md` | `main.py`, `run.py`, CORS, app factory |
| 05 | `Step_05_Database_Connection.md` | SQLAlchemy engine, session, dependency injection |
| 06 | `Step_06_Error_Handling_Architecture.md` | Global exception handlers, custom exceptions |
| 07 | `Step_07_Utility_Helpers.md` | Logger, response formatter, validation prep |
| 08 | `Step_08_Middleware_And_Health.md` | Request middleware, health check route |
| 09 | `Step_09_Testing_Workflow.md` | Test scripts for startup, DB, config, CORS |
| 10 | `Step_10_Final_Validation.md` | End-to-end checklist & server startup test |

---

## ⛔ Out of Scope (Phase 1)

- ❌ Attendance APIs
- ❌ Authentication / JWT
- ❌ Excel report generation
- ❌ Scheduler automation
- ❌ Dashboard analytics
- ❌ Student/Course models
- ❌ AI module integration

---

## 🔮 Future Scalability Considerations

1. **API versioning**: Routes will be mounted under `/api/v1/` — allows non-breaking API evolution.
2. **Database migrations**: SQLAlchemy base is set up for Alembic integration in Phase 2+.
3. **Service layer pattern**: Routes stay thin, business logic lives in `services/` — easy to unit test.
4. **Dependency injection**: FastAPI's `Depends()` makes swapping DB sessions, auth, and config effortless.
5. **Async readiness**: All database operations use `sessionmaker` compatible with async drivers if needed later.
