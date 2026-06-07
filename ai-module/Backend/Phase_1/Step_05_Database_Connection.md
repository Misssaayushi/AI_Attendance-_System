# Step 05 — Database Connection Infrastructure

## 🎯 Objective
Set up SQLAlchemy engine, session factory, declarative base, and dependency injection for DB sessions.

---

## 📝 Tasks

### 1. Create `app/database/connection.py`

**Components:**

- **Engine**: `create_engine()` with connection pooling (`pool_size=10`, `max_overflow=20`, `pool_recycle=3600`)
- **Session Factory**: `sessionmaker(autocommit=False, autoflush=False, bind=engine)`
- **`get_db()` dependency**: Generator that yields a session and closes it in `finally`
- **`test_db_connection()`**: Executes `SELECT 1` to verify DB is reachable

### 2. Create `app/database/base.py`

- Declarative base: `Base = declarative_base()` — all future models inherit from this.

### 3. MySQL Prerequisite

```sql
CREATE DATABASE IF NOT EXISTS ai_attendance_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

---

## 🧠 Key Decisions

| Decision | Rationale |
|----------|-----------|
| Sync SQLAlchemy (not async) | Simpler debugging, sufficient for <100 concurrent users |
| Connection pooling | Reused connections (~0.1ms) vs new connections (~50ms) |
| `autocommit=False` | Explicit transaction control with rollback support |
| `pool_recycle=3600` | Prevents MySQL `wait_timeout` from killing idle connections |
| `get_db()` with `yield` | Guarantees session cleanup even on route exceptions |

---

## ✅ Checklist
- [ ] `connection.py` with engine, session factory, `get_db()`, `test_db_connection()`
- [ ] `base.py` with declarative base
- [ ] MySQL database created
- [ ] Connection test passes
