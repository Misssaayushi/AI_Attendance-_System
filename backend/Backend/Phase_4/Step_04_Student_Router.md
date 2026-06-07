# Step 04 – Student Router

## Purpose
Define the FastAPI router that exposes CRUD endpoints for the Student resource under the base path `/api/v1/students`.

## Endpoints
| Method | Path | Description |
|--------|------|-------------|
| `POST`   | `/`               | Create a new student. |
| `GET`    | `/`               | List students (supports pagination & filters). |
| `GET`    | `/{student_id}`   | Retrieve a single student. |
| `PUT`    | `/{student_id}`   | Update student details. |
| `DELETE` | `/{student_id}`   | Delete a student. |

## Implementation Notes
- Use `APIRouter(prefix="/students", tags=["Students"])`.
- Depend on `get_current_admin_user` from the existing auth module.
- Return responses using the utility from **Step 09** for consistent format.
- Raise custom `StudentNotFound` or `DuplicateRollNumber` exceptions defined in **Step 08**.

## File Location
Create the router at:
`app/routes/students.py`

---
*When the router file is ready, the next step is to register it in the main application (Step 05).*
