from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class PatientCreateRequest(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    phone: str | None = None

    class Config:
        extra = "allow"


class PatientDetailResponse(BaseModel):
    patient_id: int
    first_name: str
    last_name: str
    email: str | None = None
    phone: str | None = None
    raw_data: dict[str, Any] = Field(default_factory=dict)
