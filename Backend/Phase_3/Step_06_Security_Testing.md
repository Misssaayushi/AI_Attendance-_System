# Step 06 — Security Testing

## 🎯 Objective
Verify the authentication system with automated tests in `app/tests/test_auth.py`.

---

## 📌 Implementation Details

### 1. Login Tests
- Test valid credentials (success).
- Test invalid credentials (failure).
- Test missing username/password (validation error).

### 2. Protection Tests
- Access a protected route without a token (failure).
- Access a protected route with an invalid token (failure).
- Access with a valid token (success).

---

## ✅ Checklist
- [ ] Create `app/tests/test_auth.py`.
- [ ] Implement all security test cases.
- [ ] Run and verify 100% success.
