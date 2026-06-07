# Step 02 — Relationship Mapping

## 🎯 Objective
Establish referential integrity and ORM-level relationships between tables.

---

## 📌 Implementation Details

### 1. One-to-Many (Student ↔ Attendance)
- A student can have many attendance records.
- Use `relationship("Attendance", back_populates="student", cascade="all, delete-orphan")`.
- This ensures if a student is deleted, their attendance data is cleaned up automatically.

### 2. Indexing Strategy
- Index `Attendance.date` for fast filtering in the Dashboard.
- Index `Student.roll_number` for fast lookups during AI scanning.

---

## ✅ Checklist
- [ ] Add Foreign Key constraints to `Attendance` model.
- [ ] Configure SQLAlchemy `relationship` on both sides.
- [ ] Add indexes to frequently queried columns.
