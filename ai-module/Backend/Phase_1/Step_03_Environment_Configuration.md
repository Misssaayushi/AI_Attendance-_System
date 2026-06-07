# Step 03 — Environment Configuration

## 🎯 Objective

Create a centralized configuration system using `.env` files and Pydantic-based settings that loads all environment variables at startup with validation.

---

## 📌 Why Centralized Configuration?

Hardcoding database passwords, secret keys, or API URLs directly in source code is:

- **A security risk** — credentials get committed to Git.
- **Inflexible** — changing a DB host requires code changes and redeployment.
- **Error-prone** — typos in repeated strings cause runtime failures.

Our solution: **One `.env` file** → **One `config.py` loader** → **Every module imports from `config`**.

---

## 📝 Tasks

### 1. Create `.env` File

Location: `Backend/.env`

This file holds **all environment-specific variables** and is **never committed to Git**.

```env
# ============================================
# AI ATTENDANCE SYSTEM - BACKEND CONFIGURATION
# ============================================

# --- Database Configuration ---
DB_HOST=localhost
DB_PORT=3306
DB_NAME=ai_attendance_db
DB_USER=root
DB_PASSWORD=your_password_here

# --- Server Configuration ---
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DEBUG_MODE=True

# --- Security ---
SECRET_KEY=your-secret-key-change-in-production

# --- API Settings ---
API_PREFIX=/api/v1

# --- Export Paths ---
EXPORT_DIR=./exports

# --- Logging ---
LOG_LEVEL=DEBUG
LOG_FILE=./logs/app.log
```

### 2. Create `.env.example` File

Location: `Backend/.env.example`

This is a **template** for team members — identical to `.env` but with placeholder values. This file **is committed to Git**.

```env
# Copy this file to .env and fill in your values

DB_HOST=localhost
DB_PORT=3306
DB_NAME=ai_attendance_db
DB_USER=root
DB_PASSWORD=

SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DEBUG_MODE=True

SECRET_KEY=change-this-in-production

API_PREFIX=/api/v1
EXPORT_DIR=./exports

LOG_LEVEL=DEBUG
LOG_FILE=./logs/app.log
```

### 3. Create `app/config.py`

This is the **centralized settings loader**. It uses `python-dotenv` to read `.env` and provides a single `settings` object that every module imports.

**Key Design Decisions:**

- **Dataclass-style access**: `settings.DB_HOST` instead of `os.getenv("DB_HOST")` everywhere.
- **Default values**: Safe fallbacks for non-critical settings.
- **Validation at startup**: Missing critical variables (like `DB_PASSWORD`) raise errors immediately — not when the first DB query runs 10 minutes later.
- **Single instance**: One `Settings` object created at module load time.

**What `config.py` will contain:**

```
class Settings:
    # Database settings
    DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

    # Server settings  
    SERVER_HOST, SERVER_PORT, DEBUG_MODE

    # Security
    SECRET_KEY

    # API settings
    API_PREFIX

    # Export paths
    EXPORT_DIR

    # Logging
    LOG_LEVEL, LOG_FILE

    # Computed property: DATABASE_URL
    # Format: mysql+mysqlconnector://user:pass@host:port/dbname

settings = Settings()  # Singleton instance
```

### 4. Computed Database URL

The `DATABASE_URL` is **computed** from individual components:

```
mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}
```

**Why computed?**
- Individual variables are easier to manage in `.env`.
- The full URL format is specific to SQLAlchemy — an implementation detail, not a config concern.
- Changing the DB driver (e.g., `pymysql` instead of `mysqlconnector`) only requires changing one line in `config.py`.

---

## 🧠 Design Decision: Why Not Use Pydantic `BaseSettings`?

Pydantic's `BaseSettings` is powerful but adds complexity. For a university project:

- `python-dotenv` + a simple class is **easier to understand and debug**.
- No extra dependency (`pydantic-settings` is separate from `pydantic` v2+).
- We can always migrate to `BaseSettings` later without changing the interface (`settings.DB_HOST` stays the same).

---

## 🔒 Security Notes

| Practice | Implementation |
|----------|---------------|
| Never commit `.env` | Added to `.gitignore` in Step 01 |
| Provide `.env.example` | Template with empty sensitive fields |
| Validate on startup | Missing `DB_PASSWORD` = immediate error |
| Use `SECRET_KEY` | Required for JWT auth in future phases |

---

## ✅ Completion Checklist

- [ ] `.env` file created with all configuration variables
- [ ] `.env.example` template created (Git-safe)
- [ ] `app/config.py` created with `Settings` class
- [ ] `settings` singleton instance is importable
- [ ] `DATABASE_URL` is computed correctly
- [ ] Missing critical variables raise clear error messages
- [ ] `.env` is listed in `.gitignore`
