# app/schemas/student.py
"""Pydantic schemas for Student Management API.
These models are used for request validation and response formatting.
"""

import ast
import json
import re
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class StudentBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    roll_number: str
    contact_number: Optional[str] = None
    department: str
    course: str
    year_batch: str
    semester: int
    section: Optional[str] = None
    gender: str
    face_encoding: Optional[List[float]] = None

    @field_validator("face_encoding", mode="before")
    @classmethod
    def parse_and_validate_face_encoding(cls, v):
        if v is None:
            return v

        # DB may store the encoding as JSON string in Text column.
        if isinstance(v, str):
            try:
                v = json.loads(v)
            except json.JSONDecodeError:
                # Backward compatibility for rows stored as Python-list strings.
                try:
                    v = ast.literal_eval(v)
                except (ValueError, SyntaxError):
                    # Last fallback: extract numeric tokens from legacy/raw strings.
                    nums = re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", v)
                    if nums:
                        v = [float(n) for n in nums]
                    else:
                        raise ValueError("face_encoding must be valid JSON list")

        if not isinstance(v, list):
            raise ValueError("face_encoding must be a list of float values")

        return v

    @field_validator("roll_number")
    @classmethod
    def validate_roll_number(cls, v):
        import re

        pattern = r"^[A-Za-z0-9_/-]{1,50}$"
        if not re.match(pattern, v):
            raise ValueError(
                "roll_number must be alphanumeric and between 1 to 50 characters (can contain dashes or slashes)"
            )
        return v

    @field_validator("contact_number")
    @classmethod
    def validate_contact_number(cls, v):
        if v is None:
            return v
        import re

        pattern = r"^\+?[0-9]{7,15}$"
        if not re.match(pattern, v):
            raise ValueError("contact_number must be a valid phone number between 7 to 15 digits")
        return v


class StudentCreate(StudentBase):
    @field_validator("face_encoding")
    @classmethod
    def validate_face_encoding_length(cls, v):
        if v is not None and len(v) != 128:
            raise ValueError("face_encoding must contain exactly 128 float values")
        return v


class StudentUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    roll_number: Optional[str] = None
    contact_number: Optional[str] = None
    department: Optional[str] = None
    course: Optional[str] = None
    year_batch: Optional[str] = None
    semester: Optional[int] = None
    section: Optional[str] = None
    gender: Optional[str] = None
    face_encoding: Optional[List[float]] = None

    @field_validator("face_encoding", mode="before")
    @classmethod
    def parse_and_validate_face_encoding(cls, v):
        if v is None:
            return v

        if isinstance(v, str):
            try:
                v = json.loads(v)
            except json.JSONDecodeError:
                try:
                    v = ast.literal_eval(v)
                except (ValueError, SyntaxError):
                    nums = re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", v)
                    if nums:
                        v = [float(n) for n in nums]
                    else:
                        raise ValueError("face_encoding must be valid JSON list")

        if not isinstance(v, list):
            raise ValueError("face_encoding must be a list of float values")

        return v

    @field_validator("face_encoding")
    @classmethod
    def validate_face_encoding_length(cls, v):
        if v is not None and len(v) != 128:
            raise ValueError("face_encoding must contain exactly 128 float values")
        return v

    @field_validator("roll_number")
    @classmethod
    def validate_roll_number(cls, v):
        if v is None:
            return v
        import re

        pattern = r"^[A-Za-z0-9_/-]{1,50}$"
        if not re.match(pattern, v):
            raise ValueError(
                "roll_number must be alphanumeric and between 1 to 50 characters (can contain dashes or slashes)"
            )
        return v

    @field_validator("contact_number")
    @classmethod
    def validate_contact_number(cls, v):
        if v is None:
            return v
        import re

        pattern = r"^\+?[0-9]{7,15}$"
        if not re.match(pattern, v):
            raise ValueError("contact_number must be a valid phone number between 7 to 15 digits")
        return v


class StudentResponse(StudentBase):
    # ORM model uses email_address column name, API response should expose `email`.
    email: EmailStr = Field(validation_alias="email_address")
    id: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    attendance_rate: Optional[float] = None
    status: Optional[str] = None
    arrival_time: Optional[str] = None

    @field_validator("created_at", "updated_at", mode="before")
    @classmethod
    def format_datetime(cls, v):
        from datetime import datetime

        if isinstance(v, datetime):
            return v.isoformat()
        return v

    @field_validator("face_encoding", mode="before")
    @classmethod
    def normalize_invalid_face_encoding(cls, v):
        """
        Keep list/get endpoints resilient for legacy DB rows.
        If encoding is malformed or wrong-length, return None instead of 500.
        """
        if v is None:
            return None
        if isinstance(v, str):
            try:
                v = json.loads(v)
            except Exception:
                try:
                    v = ast.literal_eval(v)
                except Exception:
                    nums = re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", v)
                    if nums:
                        v = [float(n) for n in nums]
                    else:
                        return None
        if not isinstance(v, list):
            return None
        if len(v) != 128:
            return None
        return v

    model_config = ConfigDict(from_attributes=True)


class StudentListResponse(BaseModel):
    items: List[StudentResponse]
    total: int
    page: int
    page_size: int
    pages: int
