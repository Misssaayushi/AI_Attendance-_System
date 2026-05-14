# Step 05 — Schema Testing

## 🎯 Objective
Validate the database design using automated tests.

---

## 📌 Implementation Details

### 1. Table Integrity Tests
- Verify that `Students`, `Attendance`, and `Admins` tables exist.
- Verify that constraints (Unique roll number, Foreign Keys) are working.

### 2. Relationship Tests
- Insert a student and an attendance record.
- Verify that the student can "find" their attendance via the ORM back-reference.

---

## ✅ Checklist
- [ ] Create `app/tests/test_database.py`.
- [ ] Implement tests for table creation and relationships.
- [ ] Run and verify all tests pass.
