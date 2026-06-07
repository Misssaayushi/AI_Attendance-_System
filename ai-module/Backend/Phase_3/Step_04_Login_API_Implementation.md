# Step 04 — Login API Implementation

## 🎯 Objective
Create the authentication routes in `app/routes/auth.py`.

---

## 📌 Implementation Details

### 1. `POST /auth/login`
- Accepts `LoginRequest`.
- Calls the Auth Service to validate.
- Returns `TokenResponse`.

### 2. `POST /auth/logout`
- Returns a success message.
- (Stateless logout: Instructs client to delete token).

---

## ✅ Checklist
- [ ] Create `app/routes/auth.py`.
- [ ] Implement Login and Logout routes.
- [ ] Register the auth router in `app/routes/__init__.py`.
