# Step 05 — Route Protection

## 🎯 Objective
Implement the `get_current_admin` dependency to protect future endpoints.

---

## 📌 Implementation Details

### 1. `get_current_admin` Dependency
- Extracts the Bearer token from the Request header.
- Decodes and validates the token.
- Returns the admin object or raises `401 Unauthorized`.

---

## ✅ Checklist
- [ ] Create `app/middleware/auth_deps.py`.
- [ ] Implement the `get_current_admin` dependency.
- [ ] Test protection on a dummy route.
