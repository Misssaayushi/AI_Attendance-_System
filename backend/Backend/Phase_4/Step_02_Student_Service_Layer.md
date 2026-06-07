# Step 02 – Student Service Layer

## Objective
Create a service module (`app/services/student_service.py`) that encapsulates all business logic for the Student domain. The service will be called by the FastAPI router and will use the repository layer for DB access.

## Responsibilities
- Validate input data beyond schema validation (e.g., unique email/roll number).
- Perform CRUD operations with proper transaction handling.
- Apply pagination/f filtering helpers.
- Raise domain‑specific exceptions (`StudentNotFound`, `DuplicateStudentError`).
- Prepare data for response models (e.g., hide password hashes, format timestamps).

## Design Outline
```text
StudentService
├─ create_student(dto: StudentCreateDTO) → StudentReadDTO
├─ get_student(student_id: int) → StudentReadDTO
├─ list_students(params: StudentQueryParams) → Paginated[StudentReadDTO]
├─ update_student(student_id: int, dto: StudentUpdateDTO) → StudentReadDTO
└─ delete_student(student_id: int) → None
```

## Key Functions
1. **`create_student`**
   - Check for existing email/roll number using repository.
   - Hash password if provided.
   - Persist via `student_repository.create`.
2. **`get_student`**
   - Retrieve by ID, raise `StudentNotFound` if missing.
3. **`list_students`**
   - Accept `limit`, `offset`, optional filters (`name`, `department`).
   - Return total count and list of DTOs.
4. **`update_student`**
   - Partial update; only non‑null fields are applied.
   - Re‑validate uniqueness if email/roll changed.
5. **`delete_student`**
   - Soft‑delete flag or hard delete based on project policy.

## Error Handling
All service methods raise custom exceptions defined in `app/exceptions/student_exceptions.py`. The router’s exception handlers translate these to appropriate HTTP responses.

## Dependencies
- `app.repositories.student_repository`
- `app.schemas.student`
- `app.utils.security` (password hashing)
- `app.db.session` (SQLAlchemy session management)

---
*Implementation will be added in `app/services/student_service.py` during coding phase.*
