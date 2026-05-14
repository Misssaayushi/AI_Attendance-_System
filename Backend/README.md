# AI-Based Smart Attendance System - Backend

This is the backend for the AI-Based Smart Attendance Management System, built with **FastAPI**, **SQLAlchemy**, and **MySQL**.

## 🚀 Phase 1: Infrastructure & Architecture Complete

The backend is structured using a production-grade modular architecture, prioritizing scalability and maintainability.

### 🏗️ Project Structure
```
backend/
│
├── app/
│   ├── main.py              # App factory & entry point
│   ├── config.py            # Centralized settings (Pydantic/Dotenv)
│   ├── routes/              # API Endpoints (Health check included)
│   ├── database/            # DB Engine, Session, & Base model
│   ├── middleware/          # Error handlers & Request logging
│   ├── utils/               # Logger & Response formatters
│   └── tests/               # Validation suite
│
├── logs/                    # Local runtime logs
├── .env                     # Environment variables (Private)
├── .env.example             # Environment template
├── requirements.txt         # Dependencies
└── run.py                   # Development server script
```

## 🛠️ Setup Instructions

### 1. Environment Setup
Navigate to the `Backend` folder:
```bash
cd Backend
```

Create and activate a virtual environment:
```bash
python -m venv venv
# Windows (PowerShell)
.\venv\Scripts\Activate.ps1
# Windows (CMD)
.\venv\Scripts\activate.bat
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Configuration
Copy the template and fill in your MySQL credentials:
```bash
cp .env.example .env
```

### 3. Running the Server
```bash
python run.py
```
The server will be available at `http://localhost:8000`.
- **Swagger Docs**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### 4. Running Tests
```bash
python -m pytest app/tests/test_setup.py -v
```

## 📦 Key Technologies
- **FastAPI**: Modern, high-performance web framework.
- **SQLAlchemy**: Powerful SQL toolkit and ORM.
- **MySQL Connector**: Database driver.
- **Python-Dotenv**: Configuration management.

---
*University Internship Project - Phase 1 Foundation Complete.*
