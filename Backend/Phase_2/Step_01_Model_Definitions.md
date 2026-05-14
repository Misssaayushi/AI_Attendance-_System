# Step 01 — Model Definitions

## 🎯 Objective
Define the database schema using SQLAlchemy ORM classes in `app/models/`.

---

## 📌 Implementation Details

### 1. `Student` Model
- **Primary Key**: `id` (Integer)
- **Unique Constraints**: `roll_number`, `email_address`
- **Dropdown Fields**: 
    - `gender`: (Male, Female, Other)
    - `semester`: (1 through 8)
    - `department`: (CSE, IT, ECE, ME, etc.)
- **AI Integration**: `face_encoding` (Text) - stores the numerical vector.

### 2. `Attendance` Model
- **Primary Key**: `id` (Integer)
- **Foreign Key**: `student_id` -> `students.id`
- **Columns**: `date` (Date), `time` (Time), `status` (Present/Absent/Late).

### 3. `Admin` Model
- **Columns**: `username` (Unique), `password` (Hashed storage prep).

---

## ✅ Checklist
- [ ] Create `app/models/student.py`
- [ ] Create `app/models/attendance.py`
- [ ] Create `app/models/admin.py`
- [ ] Export all models in `app/models/__init__.py`
