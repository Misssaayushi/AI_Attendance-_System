# Step 07 – Request Validation

## Goal
Define comprehensive validation logic for student‑related payloads.

### Validation Rules
- **email**: must be a valid email format (`EmailStr` from Pydantic) and unique in DB.
- **roll_number**: string, required, unique, matches pattern `^[A-Z]{2}[0-9]{4}$` (e.g., `CS2021`).
- **first_name / last_name**: non‑empty, trimmed, max 50 characters.
- **phone_number** (optional): regex `^\+?[0-9]{10,15}$`.
- **face_encoding** (optional): JSON array of 128 floats, each between `-1.0` and `1.0`.

### Implementation Sketch
```python
from pydantic import BaseModel, EmailStr, validator
from typing import List, Optional

class StudentCreate(BaseModel):
    email: EmailStr
    roll_number: str
    first_name: str
    last_name: str
    phone_number: Optional[str] = None
    face_encoding: Optional[List[float]] = None

    @validator('roll_number')
    def roll_pattern(cls, v):
        import re
        if not re.fullmatch(r'^[A-Z]{2}[0-9]{4}$', v):
            raise ValueError('Invalid roll number format')
        return v

    @validator('phone_number')
    def phone_pattern(cls, v):
        if v is None:
            return v
        import re
        if not re.fullmatch(r'^\+?[0-9]{10,15}$', v):
            raise ValueError('Invalid phone number')
        return v

    @validator('face_encoding')
    def encoding_length(cls, v):
        if v is None:
            return v
        if len(v) != 128:
            raise ValueError('face_encoding must contain 128 floats')
        return v
```

*Add similar validators for `StudentUpdate` where fields are optional.*
