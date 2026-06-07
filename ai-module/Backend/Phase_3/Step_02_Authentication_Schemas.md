# Step 02 — Authentication Schemas

## 🎯 Objective
Define request and response data models in `app/schemas/auth.py`.

---

## 📌 Implementation Details

### 1. `LoginRequest`
- `username`: str
- `password`: str

### 2. `TokenResponse`
- `access_token`: str
- `token_type`: str (usually "bearer")
- `username`: str

---

## ✅ Checklist
- [ ] Create `app/schemas/` directory.
- [ ] Create `app/schemas/auth.py`.
- [ ] Define Pydantic models for Login.
