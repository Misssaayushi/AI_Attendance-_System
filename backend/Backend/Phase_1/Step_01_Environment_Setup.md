# Step 01 — Environment Setup

## 🎯 Objective

Set up the Python development environment, create a virtual environment, and install all required dependencies.

---

## 📌 Why This Step First?

Before writing any code, we need a **clean, isolated Python environment**. A virtual environment (`venv`) ensures:

- Project dependencies don't conflict with system-wide Python packages.
- Every team member installs the **exact same versions**.
- Deployment becomes reproducible via `requirements.txt`.

---

## 📝 Tasks

### 1. Verify Python Installation

```bash
python --version
```

- **Required**: Python 3.10+ (FastAPI and modern type hints require 3.10+)

### 2. Create Virtual Environment

Navigate to the `Backend/` folder and create the venv:

```bash
cd "AI Attendance System/Backend"
python -m venv venv
```

### 3. Activate Virtual Environment

**Windows (PowerShell):**
```bash
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```bash
.\venv\Scripts\activate.bat
```

### 4. Install Required Libraries

```bash
pip install fastapi uvicorn python-dotenv python-multipart sqlalchemy mysql-connector-python openpyxl pandas apscheduler
```

### 5. Freeze Dependencies

```bash
pip freeze > requirements.txt
```

### 6. Create `.gitignore`

Create a `.gitignore` file in `Backend/` to exclude unnecessary files:

```
# Virtual Environment
venv/

# Environment Variables
.env

# Python Cache
__pycache__/
*.pyc
*.pyo

# IDE Files
.vscode/
.idea/

# Logs
logs/*.log

# OS Files
.DS_Store
Thumbs.db
```

---

## 📦 Library Purpose Reference

| Library | Purpose |
|---------|---------|
| `fastapi` | Web framework — API routing, validation, docs |
| `uvicorn` | ASGI server — runs FastAPI in development & production |
| `python-dotenv` | Loads `.env` variables into `os.environ` |
| `python-multipart` | Required for form data / file uploads in FastAPI |
| `sqlalchemy` | ORM — database models, queries, session management |
| `mysql-connector-python` | MySQL database driver for SQLAlchemy |
| `openpyxl` | Excel file generation (future Phase) |
| `pandas` | Data manipulation for reports (future Phase) |
| `apscheduler` | Task scheduling for automated attendance (future Phase) |

---

## ✅ Completion Checklist

- [ ] Python 3.10+ installed and verified
- [ ] Virtual environment created in `Backend/venv/`
- [ ] Virtual environment activated
- [ ] All 9 libraries installed successfully
- [ ] `requirements.txt` generated
- [ ] `.gitignore` created with proper exclusions

---

## ⚠️ Common Issues

| Issue | Solution |
|-------|----------|
| `pip` not found | Use `python -m pip install ...` |
| PowerShell execution policy error | Run `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` |
| MySQL connector fails to install | Ensure Microsoft Visual C++ Build Tools are installed |
| `venv` command not found | Install `python3-venv` (Linux) or reinstall Python with PATH checked (Windows) |
