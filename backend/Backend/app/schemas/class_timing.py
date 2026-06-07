from __future__ import annotations

from datetime import time, datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ValidationInfo, field_validator

class ClassTimingBase(BaseModel):
    department: Optional[str] = Field(None, description="Department for specific rules. Null for global.")
    semester: Optional[int] = Field(None, ge=1, le=8, description="Semester for specific rules. Null for global.")
    class_start_time: time
    class_end_time: time
    present_cutoff: time
    late_cutoff: time
    is_active: bool = True

class ClassTimingCreate(ClassTimingBase):
    pass

class ClassTimingUpdate(ClassTimingCreate):
    pass

class ClassTimingResponse(ClassTimingBase):
    id: int
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

class ClassTimingListResponse(BaseModel):
    items: List[ClassTimingResponse]
    total: int
