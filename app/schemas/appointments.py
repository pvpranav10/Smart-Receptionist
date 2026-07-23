from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AppointmentBookingRequest(BaseModel):
    patient_id: int
    appointment_type_id: int
    branch_name: str
    starts_at: str
    note: str | None = None
    provider_id: int | None = None


class AppointmentBookingResponse(BaseModel):
    appointment_id: int
    status: str
    starts_at: str
    location_id: int
    raw_data: dict[str, Any] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    detail: str
