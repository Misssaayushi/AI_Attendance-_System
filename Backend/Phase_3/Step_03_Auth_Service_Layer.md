# Step 03 — Auth Service Layer

## 🎯 Objective
Implement the business logic for authentication in `app/services/auth_service.py`.

---

## 📌 Implementation Details

### 1. `authenticate_admin`
- Fetch the admin from `ai_attendance_db` by username.
- Use the security utility to verify the password hash.
- Raise `UnauthorizedException` if invalid.

---

## ✅ Checklist
- [ ] Create `app/services/` directory.
- [ ] Create `app/services/auth_service.py`.
- [ ] Implement admin authentication logic.
