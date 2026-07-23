from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class PatientDetailResponse(BaseModel):
    patient_id: int
    first_name: str
    last_name: str
    email: str | None = None
    phone: str | None = None
    raw_data: dict[str, Any] = Field(default_factory=dict)
