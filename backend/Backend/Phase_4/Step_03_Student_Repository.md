# Step 03 – Student Repository

## Purpose
Create low‑level SQLAlchemy helper functions that interact directly with the `Student` model. These helpers are used by the service layer to keep business logic separate from raw DB queries.

## Content
- `get_student_by_id(db: Session, student_id: int) -> Student | None`
- `get_student_by_roll(db: Session, roll_number: str) -> Student | None`
- `list_students(db: Session, skip: int = 0, limit: int = 100, filters: dict | None = None) -> List[Student]`
- `create_student(db: Session, obj_in: StudentCreate) -> Student`
- `update_student(db: Session, db_obj: Student, obj_in: StudentUpdate) -> Student`
- `delete_student(db: Session, student_id: int) -> None`

These functions should:
1. Use the session passed in (no session management here).
2. Commit/flush only where appropriate (service layer decides transaction boundaries).
3. Raise `IntegrityError` for duplicate roll/email – let the service translate to a domain exception.
4. Accept an optional `filters` dict for dynamic WHERE clauses (e.g., name LIKE, department equality).

## Usage Example (Service Layer)
```python
from app.repositories.student_repo import get_student_by_id, create_student

student = get_student_by_id(db, student_id)
if not student:
    raise NotFoundError("Student not found")
new_student = create_student(db, student_in)
```

---
*File location:* `Backend/Phase_4/Step_03_Student_Repository.md`
