from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AppointmentSlot(BaseModel):
    appointment_id: int
    patient_name: str | None = None
    starts_at: str
    ends_at: str | None = None
    location_id: int


class AvailabilityResponse(BaseModel):
    branch_name: str | None = None
    location_id: int | None = None
    start_date: str
    end_date: str
    booked_slots: list[AppointmentSlot]
    raw_data: dict[str, Any] = Field(default_factory=dict)
