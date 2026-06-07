# Step 01 — Security Utilities

## 🎯 Objective
Implement core security helpers for password hashing and JWT management in `app/utils/security.py`.

---

## 📌 Implementation Details

### 1. Password Management
- **Library**: `passlib` with `bcrypt`.
- **Functions**:
    - `get_password_hash(password: str)`: Returns a hashed string.
    - `verify_password(plain, hashed)`: Returns True if they match.

### 2. Token Management
- **Library**: `python-jose`.
- **Functions**:
    - `create_access_token(data: dict)`: Generates a signed JWT with expiration.
    - `decode_access_token(token: str)`: Validates and returns the payload.

---

## ✅ Checklist
- [ ] Install `passlib`, `bcrypt`, and `python-jose`.
- [ ] Create `app/utils/security.py`.
- [ ] Implement hashing and JWT utilities.
