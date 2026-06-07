# Step 01 – Student Schemas

## Goal
Define Pydantic models that represent the data structures for student CRUD operations.

## Files to create
- `app/schemas/student.py`

## Models
- **StudentCreate** – fields: `first_name`, `last_name`, `email`, `roll_number`, optional `face_encoding` (list[float]).
- **StudentUpdate** – all fields optional for PATCH.
- **StudentResponse** – includes `id`, timestamps, and all create fields.

## Validation
- Email must be a valid email address.
- Roll number must be unique (handled at service layer).
- `face_encoding` must be a list of 128 floats if provided.

## Usage
These schemas will be imported by the service and router modules.
